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

    <!-- Detail -->
    <div v-else-if="event" class="flex-1 overflow-y-auto">
      <div class="mx-auto max-w-5xl p-6 space-y-4">

        <!-- Title card -->
        <div class="rounded-xl border bg-white p-6 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <h2 class="text-2xl font-bold text-ink-gray-9">{{ event.subject }}</h2>
              <p class="mt-1 text-sm text-ink-gray-5">{{ event.name }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="rounded-full px-3 py-1 text-sm font-medium" :class="statusClass(event.status)">
                {{ event.status }}
              </span>
              <Button label="Open in Desk" variant="outline" @click="openInDesk">
                <template #prefix><LucideExternalLink class="h-4 w-4" /></template>
              </Button>
            </div>
          </div>
        </div>

        <!-- 3-column grid -->
        <div class="grid grid-cols-3 gap-4">

          <!-- Schedule -->
          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">
              <LucideCalendar class="h-4 w-4" /> Schedule
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Starts On</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ formatDate(event.starts_on) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Ends On</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ formatDate(event.ends_on) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Duration</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ duration }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">All Day</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.all_day ? 'Yes' : 'No' }}</span>
              </div>
            </div>
          </div>

          <!-- Event Details -->
          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">
              <LucideInfo class="h-4 w-4" /> Details
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Type</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.event_type || '—' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Category</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.event_category || '—' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Location</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.location || '—' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Visibility</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.event_type || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Organization -->
          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">
              <LucideBuilding2 class="h-4 w-4" /> Organization
            </h3>
            <div v-if="orgDetails" class="space-y-3">
              <div class="flex items-center gap-3 mb-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold text-lg">
                  {{ orgDetails.name?.charAt(0) || '?' }}
                </div>
                <div>
                  <p class="font-semibold text-ink-gray-9">{{ orgDetails.name }}</p>
                  <p class="text-xs text-ink-gray-5">{{ orgDetails.industry || 'Organization' }}</p>
                </div>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Website</span>
                <a v-if="orgDetails.website" :href="orgDetails.website" target="_blank" class="text-sm text-blue-600 hover:underline truncate max-w-[120px]">
                  {{ orgDetails.website }}
                </a>
                <span v-else class="text-sm text-ink-gray-3">—</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Territory</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ orgDetails.territory || '—' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Annual Revenue</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ orgDetails.annual_revenue ? '₹ ' + Number(orgDetails.annual_revenue).toLocaleString() : '—' }}</span>
              </div>
            </div>
            <div v-else-if="event.reference_docname" class="space-y-2">
              <p class="text-sm text-ink-gray-6">{{ event.reference_doctype }}</p>
              <p class="font-medium text-ink-gray-9">{{ event.reference_docname }}</p>
            </div>
            <div v-else class="flex flex-col items-center justify-center py-4 text-ink-gray-3">
              <LucideBuilding2 class="h-8 w-8 mb-2 opacity-30" />
              <p class="text-sm">No organization linked</p>
            </div>
          </div>
        </div>

        <!-- Attendees full section -->
        <div class="rounded-xl border bg-white p-5 shadow-sm">
          <h3 class="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">
            <LucideUsers class="h-4 w-4" /> Attendees
            <span class="ml-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
              {{ participants.length }}
            </span>
          </h3>
          <div v-if="participants.length" class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            <div
              v-for="p in participants"
              :key="p.reference_docname"
              class="flex items-center gap-3 rounded-lg border p-3"
            >
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-semibold text-sm">
                {{ avatarLetter(p.reference_docname) }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-ink-gray-9">
                  {{ p.reference_docname?.split('@')[0] || p.reference_docname }}
                </p>
                <p class="truncate text-xs text-ink-gray-5">{{ p.reference_docname }}</p>
              </div>
            </div>
          </div>
          <div v-else class="flex items-center gap-2 text-sm text-ink-gray-3">
            <LucideUsers class="h-4 w-4" />
            No attendees added
          </div>
        </div>

        <!-- Description -->
        <div v-if="event.description" class="rounded-xl border bg-white p-5 shadow-sm">
          <h3 class="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">
            <LucideFileText class="h-4 w-4" /> Description
          </h3>
          <div class="prose prose-sm max-w-none text-ink-gray-7" v-html="event.description" />
        </div>

      </div>
    </div>

    <!-- Not found -->
    <div v-else class="flex flex-1 flex-col items-center justify-center gap-3 text-ink-gray-5">
      <LucidePresentation class="h-16 w-16 opacity-30" />
      <p class="text-lg font-medium">Event not found</p>
      <Button label="Go Back" @click="goBack" />
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
import LucideFileText from '~icons/lucide/file-text'

const props = defineProps({ eventId: String })
const router = useRouter()
const event = ref(null)
const orgDetails = ref(null)
const loading = ref(true)

// Fetch event with all fields including child table
const eventResource = createResource({
  url: 'frappe.client.get',
  params: { doctype: 'Event', name: props.eventId },
  onSuccess(data) {
    event.value = data
    loading.value = false
    // If linked to a CRM Organization, fetch it
    if (data.reference_doctype === 'CRM Organization' && data.reference_docname) {
      fetchOrg(data.reference_docname)
    }
  },
  onError() { loading.value = false },
})

function fetchOrg(name) {
  const orgResource = createResource({
    url: 'frappe.client.get',
    params: { doctype: 'CRM Organization', name },
    onSuccess(data) { orgDetails.value = data },
  })
  orgResource.fetch()
}

onMounted(() => eventResource.fetch())

// Attendees from event_participants child table
const participants = computed(() => event.value?.event_participants || [])

// Duration between start and end
const duration = computed(() => {
  if (!event.value?.starts_on || !event.value?.ends_on) return '—'
  const diff = new Date(event.value.ends_on) - new Date(event.value.starts_on)
  const mins = Math.round(diff / 60000)
  if (mins < 60) return `${mins} min`
  const hrs = Math.floor(mins / 60)
  const rem = mins % 60
  return rem ? `${hrs}h ${rem}m` : `${hrs}h`
})

function goBack() { router.push({ name: 'Product Demo' }) }
function openInDesk() { window.open(`/desk/event/${props.eventId}`, '_blank') }

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
    Cancelled: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700'
}

function avatarLetter(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}
</script>
