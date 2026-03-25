<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Product Demo" />
    </template>
    <template #right-header>
      <Button label="Schedule Event" variant="solid" @click="openNewEvent">
        <template #prefix><LucideCalendarPlus class="h-4 w-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="events"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Event"
    :options="{ allowedViews: ['list'] }"
  />
  <ProductDemoListView
    v-if="events.data && rows.length"
    ref="productDemoListView"
    v-model="events.data.page_length_count"
    :rows="rows"
    :columns="columns"
    :options="{
      resizeColumn: true,
      rowCount: events.data.row_count,
      totalCount: events.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
  />
  <EmptyState
    v-else-if="events.data && !rows.length"
    name="Product Demo"
    icon="calendar"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import ProductDemoListView from '@/components/ListViews/ProductDemoListView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import LucideCalendarPlus from '~icons/lucide/calendar-plus'
import { createResource, Button } from 'frappe-ui'
import { formatDate, timeAgo } from '@/utils'
import { ref, computed, reactive, watch } from 'vue'

const viewControls = ref(null)
const productDemoListView = ref(null)

const events = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)

// Enrichment data keyed by event name (org name + attendees)
const orgNames = reactive({})    // { [eventName]: orgNameString }
const attendees = reactive({})   // { [eventName]: ['Name1', 'Name2'] }

const FALLBACK_KEYS = new Set(['name', 'modified'])

const columns = computed(() => {
  const viewCols = (events.value?.data?.columns || []).filter(
    (c) => !FALLBACK_KEYS.has(c.key || c.value),
  )
  // Default columns – CustomEvent.default_list_data() provides these
  const base = viewCols.length
    ? viewCols
    : [
        { key: 'subject',    label: 'Subject',   type: 'Data',     width: '18rem' },
        { key: 'event_type', label: 'Type',      type: 'Data',     width: '8rem'  },
        { key: 'status',     label: 'Status',    type: 'Select',   width: '10rem' },
        { key: 'starts_on',  label: 'Starts On', type: 'Datetime', width: '12rem' },
      ]
  const enriched = [
    { key: '_orgName',   label: 'Organization', type: 'Data', width: '12rem' },
    { key: '_attendees', label: 'Attendees',    type: 'Data', width: '16rem' },
  ]
  const existing = new Set(base.map((c) => c.key || c.value))
  return [...base, ...enriched.filter((c) => !existing.has(c.key))]
})

// rows: built directly from events.data.data (which now has full fields via CustomEvent.default_list_data)
// _orgName and _attendees are patched in from reactive maps once enrichment arrives.
const rows = computed(() =>
  (events.value?.data?.data || []).map((e) => ({
    name:       e.name,
    subject:    { label: e.subject    || '' },
    event_type: { label: e.event_type || '' },
    status:     { label: e.status     || '', color: statusColor(e.status) },
    starts_on:  e.starts_on
      ? { label: formatDate(e.starts_on, '', true, true), timeAgo: __(timeAgo(e.starts_on)) }
      : { label: '' },
    _orgName:   { label: orgNames[e.name]   ?? null },
    _attendees: attendees[e.name] || [],
  })),
)

// Kick off enrichment (org name + attendees) whenever the list refreshes
watch(
  () => events.value?.data?.data,
  (stubs) => {
    if (!stubs?.length) return
    const names = stubs.map((s) => s.name)
    fetchOrgNames(stubs)
    fetchAttendees(names)
  },
  { immediate: true },
)

// ── Org name: resolve from the linked CRM Deal ──
function fetchOrgNames(stubs) {
  const dealMap = {}
  stubs.forEach((s) => {
    if (s.reference_doctype === 'CRM Deal' && s.reference_docname) {
      dealMap[s.reference_docname] = s.name
    }
  })
  const dealNames = Object.keys(dealMap)
  if (!dealNames.length) return

  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'CRM Deal',
      filters: [['name', 'in', dealNames]],
      fields: ['name', 'organization_name', 'organization'],
      limit: dealNames.length + 5,
    },
    onSuccess(deals) {
      ;(deals || []).forEach((d) => {
        const eventName = dealMap[d.name]
        if (eventName) {
          orgNames[eventName] = d.organization_name || d.organization || d.name
        }
      })
    },
  }).fetch()
}

// ── Attendees: resolve display names via existing API ──
function fetchAttendees(eventNames) {
  createResource({
    url: 'crm.api.event.get_event_participants',
    params: { event_names: eventNames },
    onSuccess(result) {
      const participantRows = Object.values(result || {}).flat()
      const contactNames = [...new Set(participantRows.filter((r) => r.reference_doctype === 'Contact'  && r.reference_docname).map((r) => r.reference_docname))]
      const userEmails   = [...new Set(participantRows.filter((r) => r.reference_doctype === 'User'     && r.reference_docname).map((r) => r.reference_docname))]
      const leadNames    = [...new Set(participantRows.filter((r) => r.reference_doctype === 'CRM Lead' && r.reference_docname).map((r) => r.reference_docname))]
      resolveAttendeeNames(result || {}, contactNames, userEmails, leadNames)
    },
  }).fetch()
}

function resolveAttendeeNames(participantMap, contactNames, userEmails, leadNames) {
  const nameMap = {}
  let pending = 0

  function apply() {
    Object.entries(participantMap).forEach(([eventName, parts]) => {
      attendees[eventName] = (parts || []).map((p) => {
        if (nameMap[p.reference_docname]) return nameMap[p.reference_docname]
        if (p.email) return p.email.split('@')[0]
        return p.reference_docname || '—'
      })
    })
  }

  function done() { if (--pending <= 0) apply() }

  function fetchNames(doctype, filters, field, fallback) {
    pending++
    createResource({
      url: 'frappe.client.get_list',
      params: { doctype, filters, fields: ['name', field], limit: 200 },
      onSuccess(docs) {
        ;(docs || []).forEach((d) => { nameMap[d.name] = d[field] || fallback(d) })
        done()
      },
      onError() { done() },
    }).fetch()
  }

  if (!contactNames.length && !userEmails.length && !leadNames.length) { apply(); return }
  if (contactNames.length) fetchNames('Contact',  [['name', 'in', contactNames]], 'full_name', (d) => d.name)
  if (userEmails.length)   fetchNames('User',      [['name', 'in', userEmails]],   'full_name', (d) => d.name.split('@')[0])
  if (leadNames.length)    fetchNames('CRM Lead',  [['name', 'in', leadNames]],    'lead_name', (d) => [d.first_name, d.last_name].filter(Boolean).join(' ') || d.name)
}

function statusColor(status) {
  return { Open: 'orange', Completed: 'green', Closed: 'green', Cancelled: 'red' }[status] || 'gray'
}

function openNewEvent() {
  window.open('/desk/event/new-event-1', '_blank')
}
</script>
