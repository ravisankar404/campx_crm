<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <Button variant="ghost" @click="goBack">
        <template #prefix><LucideArrowLeft class="h-4 w-4" /></template>
        Product Demo
      </Button>
      <span class="text-ink-gray-4">/</span>
      <span class="font-medium text-ink-gray-9">{{ event?.subject || eventId }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-ink-gray-5">Loading event...</div>
    </div>

    <!-- Not found -->
    <div v-else-if="!event" class="flex flex-1 flex-col items-center justify-center gap-3 text-ink-gray-5">
      <LucidePresentation class="h-16 w-16 opacity-30" />
      <p class="text-lg font-medium">Event not found</p>
      <Button label="Go Back" @click="goBack" />
    </div>

    <!-- Detail -->
    <div v-else class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="mx-auto max-w-5xl p-5 space-y-4">

        <!-- ── Title card ── -->
        <div class="rounded-xl border bg-surface-white p-5 shadow-sm">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-bold text-lg">
                {{ event.subject?.charAt(0)?.toUpperCase() }}
              </div>
              <div>
                <h2 class="text-xl font-bold text-ink-gray-9">{{ event.subject }}</h2>
                <p class="text-xs text-ink-gray-4 mt-0.5">{{ event.name }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusClass(event.status)">
                {{ event.status }}
              </span>
              <Button label="Open in Desk" variant="outline" @click="openInDesk">
                <template #prefix><LucideExternalLink class="h-3.5 w-3.5" /></template>
              </Button>
            </div>
          </div>
        </div>

        <!-- ── 3-col info grid ── -->
        <div class="grid grid-cols-3 gap-4">

          <!-- Schedule -->
          <div class="rounded-xl border bg-surface-white p-4 shadow-sm">
            <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
              <LucideCalendar class="h-3.5 w-3.5" /> Schedule
            </h3>
            <dl class="space-y-2">
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Starts On</dt>
                <dd class="font-medium text-ink-gray-9 text-right">{{ formatDate(event.starts_on) }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Ends On</dt>
                <dd class="font-medium text-ink-gray-9 text-right">{{ formatDate(event.ends_on) }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Duration</dt>
                <dd class="font-semibold text-indigo-600 dark:text-indigo-400">{{ duration }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">All Day</dt>
                <dd class="font-medium text-ink-gray-9">{{ event.all_day ? 'Yes' : 'No' }}</dd>
              </div>
              <div v-if="event.location" class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Location</dt>
                <dd class="font-medium text-ink-gray-9 text-right truncate max-w-[130px]">{{ event.location }}</dd>
              </div>
            </dl>
          </div>

          <!-- Details -->
          <div class="rounded-xl border bg-surface-white p-4 shadow-sm">
            <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
              <LucideInfo class="h-3.5 w-3.5" /> Details
            </h3>
            <dl class="space-y-2">
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Type</dt>
                <dd class="font-medium text-ink-gray-9">{{ event.event_type || '—' }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Category</dt>
                <dd class="font-medium text-ink-gray-9">{{ event.event_category || '—' }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Linked To</dt>
                <dd class="font-medium text-ink-gray-9 text-right text-xs">{{ event.reference_doctype || '—' }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Created By</dt>
                <dd class="font-medium text-ink-gray-9 text-right text-xs">{{ event.owner || '—' }}</dd>
              </div>
              <div class="flex justify-between text-sm">
                <dt class="text-ink-gray-5">Modified</dt>
                <dd class="font-medium text-ink-gray-9 text-right text-xs">{{ formatDate(event.modified) }}</dd>
              </div>
            </dl>
          </div>

          <!-- Organization (resolved from Deal) -->
          <div class="rounded-xl border bg-surface-white p-4 shadow-sm">
            <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
              <LucideBuilding2 class="h-3.5 w-3.5" /> Organization
            </h3>
            <!-- Loading org -->
            <div v-if="orgLoading" class="text-xs text-ink-gray-4">Loading...</div>
            <!-- Org details from linked Deal -->
            <div v-else-if="deal" class="space-y-2">
              <div class="flex items-center gap-2 mb-3">
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 font-bold">
                  {{ (deal.organization_name || deal.organization || '?').charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="font-semibold text-ink-gray-9 text-sm">{{ deal.organization_name || deal.organization || '—' }}</p>
                  <p class="text-xs text-ink-gray-4">{{ deal.name }}</p>
                </div>
              </div>
              <dl class="space-y-2">
                <div class="flex justify-between text-sm">
                  <dt class="text-ink-gray-5">Deal Status</dt>
                  <dd>
                    <span class="rounded-full px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                      {{ deal.status || '—' }}
                    </span>
                  </dd>
                </div>
                <div class="flex justify-between text-sm">
                  <dt class="text-ink-gray-5">Deal Owner</dt>
                  <dd class="font-medium text-ink-gray-9 text-xs">{{ deal.deal_owner || '—' }}</dd>
                </div>
              </dl>
              <Button
                class="mt-2 w-full"
                variant="subtle"
                @click="openDeal"
              >
                <template #prefix><LucideExternalLink class="h-3.5 w-3.5" /></template>
                View Deal
              </Button>
            </div>
            <!-- No org linked -->
            <div v-else class="flex flex-col items-center justify-center py-4 text-ink-gray-3">
              <LucideBuilding2 class="h-8 w-8 mb-1 opacity-20" />
              <p class="text-xs">No organization linked</p>
            </div>
          </div>
        </div>

        <!-- ── Attendees ── -->
        <div class="rounded-xl border bg-surface-white p-4 shadow-sm">
          <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
            <LucideUsers class="h-3.5 w-3.5" /> Attendees
            <span class="ml-1 rounded-full bg-indigo-100 px-2 py-0.5 text-xs text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold">
              {{ participants.length }}
            </span>
          </h3>
          <div v-if="participants.length" class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
            <div
              v-for="p in participants"
              :key="p.name || p.reference_docname"
              class="flex items-center gap-2.5 rounded-lg border px-3 py-2"
            >
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-bold text-sm">
                {{ resolveDisplayName(p).charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-ink-gray-9">
                  {{ resolveDisplayName(p) }}
                </p>
                <!-- Show email if available and different from display name -->
                <p v-if="p.email" class="truncate text-xs text-ink-gray-4">{{ p.email }}</p>
                <!-- Fallback: show reference_docname as subtitle for non-email types -->
                <p v-else-if="p.reference_doctype !== 'User'" class="truncate text-xs text-ink-gray-4">
                  {{ p.reference_doctype }}
                </p>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-ink-gray-3">No attendees added to this event.</p>
        </div>

        <!-- ── Activity / Remarks Log ── -->
        <div class="rounded-xl border bg-surface-white p-4 shadow-sm">
          <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
            <LucideMessageSquare class="h-3.5 w-3.5" /> Activity & Remarks
            <span v-if="comments.length" class="ml-1 rounded-full bg-surface-gray-2 px-2 py-0.5 text-xs text-ink-gray-6">
              {{ comments.length }}
            </span>
          </h3>

          <!-- Comments list -->
          <div v-if="comments.length" class="space-y-3">
            <div
              v-for="c in comments"
              :key="c.name"
              class="flex gap-3"
            >
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface-gray-2 text-ink-gray-6 text-xs font-bold mt-0.5">
                {{ (c.comment_by || 'S').charAt(0).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-sm font-semibold text-ink-gray-9">{{ c.comment_by || 'System' }}</span>
                  <span class="text-xs text-ink-gray-4">{{ formatDate(c.creation) }}</span>
                  <span
                    v-if="c.comment_type && c.comment_type !== 'Comment'"
                    class="rounded bg-surface-gray-2 px-1.5 py-0.5 text-xs text-ink-gray-5"
                  >{{ c.comment_type }}</span>
                </div>
                <div class="text-sm text-ink-gray-7 rounded-lg bg-surface-gray-1 px-3 py-2 border" v-html="c.content" />
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-ink-gray-3">No remarks or activity logged yet.</p>
        </div>

        <!-- ── Description ── -->
        <div v-if="event.description" class="rounded-xl border bg-surface-white p-4 shadow-sm">
          <h3 class="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-ink-gray-4">
            <LucideFileText class="h-3.5 w-3.5" /> Description
          </h3>
          <div class="prose prose-sm max-w-none text-ink-gray-7" v-html="event.description" />
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideExternalLink from '~icons/lucide/external-link'
import LucidePresentation from '~icons/lucide/presentation'
import LucideCalendar from '~icons/lucide/calendar'
import LucideInfo from '~icons/lucide/info'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideUsers from '~icons/lucide/users'
import LucideMessageSquare from '~icons/lucide/message-square'
import LucideFileText from '~icons/lucide/file-text'

const props = defineProps({ eventId: String })
const router = useRouter()

const event = ref(null)
const deal = ref(null)
const comments = ref([])
// nameMap: keyed by reference_docname (Contact name, User email, Lead name, etc.)
// value: human-readable display name
const nameMap = ref({})
const loading = ref(true)
const orgLoading = ref(false)

// ── Fetch Event ──
createResource({
  url: 'frappe.client.get',
  params: { doctype: 'Event', name: props.eventId },
  onSuccess(data) {
    event.value = data
    loading.value = false

    // Resolve linked deal for org info
    if (data.reference_doctype === 'CRM Deal' && data.reference_docname) {
      fetchDeal(data.reference_docname)
    }

    // Batch-fetch names for all participant types
    const parts = data.event_participants || []
    fetchParticipantNames(parts)

    // Fetch activity/comments
    fetchComments()
  },
  onError() { loading.value = false },
}).fetch()

// ── Fetch linked CRM Deal ──
function fetchDeal(dealName) {
  orgLoading.value = true
  createResource({
    url: 'frappe.client.get',
    params: { doctype: 'CRM Deal', name: dealName },
    onSuccess(data) {
      deal.value = data
      orgLoading.value = false
    },
    onError() { orgLoading.value = false },
  }).fetch()
}

// ── Fetch names for all participant types (Contact, User, Lead, etc.) ──
function fetchParticipantNames(parts) {
  if (!parts.length) return

  const contactNames = [...new Set(
    parts.filter(p => p.reference_doctype === 'Contact' && p.reference_docname)
         .map(p => p.reference_docname)
  )]
  const userEmails = [...new Set(
    parts.filter(p => p.reference_doctype === 'User' && p.reference_docname)
         .map(p => p.reference_docname)
  )]
  const leadNames = [...new Set(
    parts.filter(p => p.reference_doctype === 'CRM Lead' && p.reference_docname)
         .map(p => p.reference_docname)
  )]

  if (contactNames.length) {
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Contact',
        filters: [['name', 'in', contactNames]],
        fields: ['name', 'full_name'],
        limit: 100,
      },
      onSuccess(contacts) {
        const map = { ...nameMap.value }
        ;(contacts || []).forEach(c => { map[c.name] = c.full_name || c.name })
        nameMap.value = map
      },
    }).fetch()
  }

  if (userEmails.length) {
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'User',
        filters: [['name', 'in', userEmails]],
        fields: ['name', 'full_name'],
        limit: 100,
      },
      onSuccess(users) {
        const map = { ...nameMap.value }
        ;(users || []).forEach(u => { map[u.name] = u.full_name || u.name.split('@')[0] })
        nameMap.value = map
      },
    }).fetch()
  }

  if (leadNames.length) {
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'CRM Lead',
        filters: [['name', 'in', leadNames]],
        fields: ['name', 'lead_name', 'first_name', 'last_name'],
        limit: 100,
      },
      onSuccess(leads) {
        const map = { ...nameMap.value }
        ;(leads || []).forEach(l => {
          map[l.name] = l.lead_name
            || [l.first_name, l.last_name].filter(Boolean).join(' ')
            || l.name
        })
        nameMap.value = map
      },
    }).fetch()
  }
}

// ── Fetch comments / remarks ──
function fetchComments() {
  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Comment',
      filters: [
        ['reference_doctype', '=', 'Event'],
        ['reference_name', '=', props.eventId],
      ],
      fields: ['name', 'content', 'comment_by', 'creation', 'comment_type'],
      order_by: 'creation asc',
      limit: 100,
    },
    onSuccess(data) { comments.value = data || [] },
  }).fetch()
}

// ── Computed ──
const participants = computed(() => event.value?.event_participants || [])

const duration = computed(() => {
  if (!event.value?.starts_on || !event.value?.ends_on) return '—'
  const mins = Math.round((new Date(event.value.ends_on) - new Date(event.value.starts_on)) / 60000)
  if (mins <= 0) return '—'
  if (mins < 60) return `${mins} min`
  const hrs = Math.floor(mins / 60)
  const rem = mins % 60
  return rem ? `${hrs}h ${rem}m` : `${hrs}h`
})

// ── Resolve display name for a participant ──
// Priority: nameMap lookup > email field > reference_docname (trimmed)
function resolveDisplayName(p) {
  if (!p) return '—'
  if (nameMap.value[p.reference_docname]) return nameMap.value[p.reference_docname]
  if (p.email) return p.email.split('@')[0]
  if (p.reference_docname) return p.reference_docname
  return '—'
}

// ── Helpers ──
function goBack() { router.push({ name: 'Product Demo' }) }
function openInDesk() { window.open(`/desk/event/${props.eventId}`, '_blank') }
function openDeal() {
  if (event.value?.reference_docname) {
    window.open(`/crm/deals/${event.value.reference_docname}`, '_blank')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function statusClass(status) {
  return {
    Open: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
    Closed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    Completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    Cancelled: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  }[status] || 'bg-surface-gray-2 text-ink-gray-7'
}
</script>
