<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <h1 class="text-xl font-semibold text-ink-gray-9">Product Demo</h1>
      <Button label="Schedule Event" variant="solid" @click="openNewEvent">
        <template #prefix><LucideCalendarPlus class="h-4 w-4" /></template>
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-ink-gray-5">Loading events...</div>
    </div>

    <!-- Empty -->
    <div v-else-if="!eventRows.length" class="flex flex-1 flex-col items-center justify-center gap-3 text-ink-gray-5">
      <LucidePresentation class="h-16 w-16 opacity-30" />
      <p class="text-lg font-medium">No Product Demo events yet</p>
      <p class="text-sm">Click "Schedule Event" to create your first demo.</p>
    </div>

    <!-- Table -->
    <div v-else class="flex-1 overflow-y-auto p-5">
      <div class="overflow-hidden rounded-lg border">
        <!-- Header -->
        <div class="grid grid-cols-12 gap-3 border-b bg-surface-gray-1 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">
          <div class="col-span-3">Subject</div>
          <div class="col-span-2">Organization</div>
          <div class="col-span-3">Attendees</div>
          <div class="col-span-1">Type</div>
          <div class="col-span-1">Status</div>
          <div class="col-span-2">Starts On</div>
        </div>

        <!-- Rows -->
        <div
          v-for="event in eventRows"
          :key="event.name"
          class="grid cursor-pointer grid-cols-12 items-center gap-3 border-b px-4 py-3 last:border-b-0 hover:bg-surface-gray-1 transition-colors"
          @click="openEvent(event.name)"
        >
          <!-- Subject -->
          <div class="col-span-3 font-medium text-ink-gray-9 truncate">{{ event.subject }}</div>

          <!-- Organization Name (resolved from Deal) -->
          <div class="col-span-2 text-sm truncate">
            <span v-if="event._orgName" class="flex items-center gap-1 text-ink-gray-7">
              <LucideBuilding2 class="h-3 w-3 shrink-0 text-ink-gray-4" />
              {{ event._orgName }}
            </span>
            <span v-else class="text-ink-gray-3">—</span>
          </div>

          <!-- Attendees -->
          <div class="col-span-3">
            <div v-if="event._attendees && event._attendees.length" class="flex flex-wrap gap-1">
              <span
                v-for="a in event._attendees.slice(0, 3)"
                :key="a"
                class="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
              >{{ a }}</span>
              <span v-if="event._attendees.length > 3" class="text-xs text-ink-gray-4">
                +{{ event._attendees.length - 3 }} more
              </span>
            </div>
            <span v-else class="text-xs text-ink-gray-3">No attendees</span>
          </div>

          <!-- Type -->
          <div class="col-span-1 text-sm text-ink-gray-6">{{ event.event_type || '—' }}</div>

          <!-- Status -->
          <div class="col-span-1">
            <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium" :class="statusClass(event.status)">
              {{ event.status }}
            </span>
          </div>

          <!-- Date -->
          <div class="col-span-2 text-sm text-ink-gray-6">{{ formatDate(event.starts_on) }}</div>
        </div>
      </div>

      <div class="mt-3 text-right text-xs text-ink-gray-4">Showing {{ eventRows.length }} events</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import LucidePresentation from '~icons/lucide/presentation'
import LucideCalendarPlus from '~icons/lucide/calendar-plus'
import LucideBuilding2 from '~icons/lucide/building-2'

const router = useRouter()

// Raw data
const rawEvents = ref([])
const orgMap = ref({})    // dealName → organization_name
const attendeesMap = ref({}) // eventName → [full_name, ...]
const userMap = ref({})   // email → full_name
const loading = ref(true)

// Step 1: Fetch events
const eventsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Event',
    fields: ['name', 'subject', 'starts_on', 'ends_on', 'status', 'event_type',
             'event_category', 'location', 'reference_doctype', 'reference_docname'],
    order_by: 'starts_on desc',
    limit: 50,
  },
  onSuccess(data) {
    rawEvents.value = data || []
    if (data && data.length) {
      fetchDealOrgs(data)
      fetchParticipants(data.map(e => e.name))
    } else {
      loading.value = false
    }
  },
  onError() { loading.value = false },
})

// Step 2: Fetch org names from linked CRM Deals
function fetchDealOrgs(events) {
  const dealNames = [...new Set(
    events.filter(e => e.reference_doctype === 'CRM Deal' && e.reference_docname)
          .map(e => e.reference_docname)
  )]
  if (!dealNames.length) { loading.value = false; return }

  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'CRM Deal',
      filters: [['name', 'in', dealNames]],
      fields: ['name', 'organization_name', 'organization'],
      limit: 100,
    },
    onSuccess(deals) {
      const map = {}
      deals.forEach(d => { map[d.name] = d.organization_name || d.organization || d.name })
      orgMap.value = map
      loading.value = false
    },
    onError() { loading.value = false },
  }).fetch()
}

// Step 3: Fetch all participants for listed events
function fetchParticipants(eventNames) {
  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Event Participants',
      filters: [['parent', 'in', eventNames]],
      fields: ['parent', 'reference_docname', 'reference_doctype'],
      limit: 500,
    },
    onSuccess(rows) {
      // Collect unique user emails
      const emails = [...new Set(
        rows.filter(r => r.reference_doctype === 'User').map(r => r.reference_docname)
      )]
      // Build event → attendees map (use email for now, resolved later)
      const map = {}
      rows.forEach(r => {
        if (!map[r.parent]) map[r.parent] = []
        map[r.parent].push(r.reference_docname)
      })
      attendeesMap.value = map
      if (emails.length) fetchUserNames(emails)
    },
  }).fetch()
}

// Step 4: Fetch full names of users
function fetchUserNames(emails) {
  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'User',
      filters: [['name', 'in', emails]],
      fields: ['name', 'full_name'],
      limit: 200,
    },
    onSuccess(users) {
      const map = {}
      users.forEach(u => { map[u.name] = u.full_name || u.name.split('@')[0] })
      userMap.value = map
    },
  }).fetch()
}

onMounted(() => eventsResource.fetch())

const eventRows = computed(() =>
  rawEvents.value.map(e => ({
    ...e,
    _orgName: e.reference_doctype === 'CRM Deal'
      ? orgMap.value[e.reference_docname] || null
      : (e.reference_doctype === 'CRM Organization' ? e.reference_docname : null),
    _attendees: (attendeesMap.value[e.name] || []).map(email =>
      userMap.value[email] || email.split('@')[0]
    ),
  }))
)

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function statusClass(status) {
  return {
    Open: 'bg-orange-100 text-orange-700',
    Closed: 'bg-green-100 text-green-700',
    Completed: 'bg-green-100 text-green-700',
    Cancelled: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700'
}

function openEvent(name) {
  router.push({ name: 'Product Demo Event', params: { eventId: name } })
}

function openNewEvent() {
  window.open('/desk/event/new-event-1', '_blank')
}
</script>
