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
    <div v-if="events.list.loading" class="flex flex-1 items-center justify-center">
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

          <!-- Organization -->
          <div class="col-span-2 text-sm text-ink-gray-6 truncate">
            <span v-if="event.reference_doctype === 'CRM Organization'" class="flex items-center gap-1">
              <LucideBuilding2 class="h-3 w-3 shrink-0" />
              {{ event.reference_docname }}
            </span>
            <span v-else-if="event.reference_docname" class="text-ink-gray-4 text-xs">
              {{ event.reference_doctype }}: {{ event.reference_docname }}
            </span>
            <span v-else class="text-ink-gray-3">—</span>
          </div>

          <!-- Attendees -->
          <div class="col-span-3">
            <div v-if="event._participants && event._participants.length" class="flex flex-wrap gap-1">
              <span
                v-for="p in event._participants.slice(0, 3)"
                :key="p"
                class="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
              >
                {{ p }}
              </span>
              <span v-if="event._participants.length > 3" class="text-xs text-ink-gray-4">
                +{{ event._participants.length - 3 }} more
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createListResource, createResource, Button } from 'frappe-ui'
import LucidePresentation from '~icons/lucide/presentation'
import LucideCalendarPlus from '~icons/lucide/calendar-plus'
import LucideBuilding2 from '~icons/lucide/building-2'

const router = useRouter()
const participantsMap = ref({})

const events = createListResource({
  doctype: 'Event',
  fields: ['name', 'subject', 'starts_on', 'ends_on', 'status', 'event_type', 'event_category', 'location', 'reference_doctype', 'reference_docname'],
  orderBy: 'starts_on desc',
  pageLength: 50,
  auto: true,
  onSuccess(data) {
    // Fetch participants for all events
    if (data && data.length) {
      fetchAllParticipants(data.map(e => e.name))
    }
  },
})

const eventRows = computed(() => {
  return (events.list?.data || []).map(e => ({
    ...e,
    _participants: participantsMap.value[e.name] || [],
  }))
})

function fetchAllParticipants(eventNames) {
  const participantsResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Event Participants',
      filters: [['parent', 'in', eventNames]],
      fields: ['parent', 'reference_docname'],
      limit: 500,
    },
    onSuccess(rows) {
      const map = {}
      rows.forEach(r => {
        if (!map[r.parent]) map[r.parent] = []
        // Show short name (email before @)
        const short = r.reference_docname?.includes('@')
          ? r.reference_docname.split('@')[0]
          : r.reference_docname
        map[r.parent].push(short)
      })
      participantsMap.value = map
    },
  })
  participantsResource.fetch()
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
    Open: 'bg-orange-100 text-orange-700',
    Closed: 'bg-green-100 text-green-700',
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
