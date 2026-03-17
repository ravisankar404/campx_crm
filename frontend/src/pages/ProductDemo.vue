<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <h1 class="text-xl font-semibold text-ink-gray-9">Product Demo</h1>
      <Button
        label="Schedule Event"
        variant="solid"
        @click="openNewEvent"
      >
        <template #prefix>
          <LucideCalendarPlus class="h-4 w-4" />
        </template>
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="events.list.loading" class="flex flex-1 items-center justify-center">
      <div class="text-ink-gray-5">Loading events...</div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="!events.list.loading && !eventRows.length"
      class="flex flex-1 flex-col items-center justify-center gap-3 text-ink-gray-5"
    >
      <LucidePresentation class="h-16 w-16 opacity-30" />
      <p class="text-lg font-medium">No Product Demo events yet</p>
      <p class="text-sm">Click "Schedule Event" to create your first demo.</p>
    </div>

    <!-- Event List -->
    <div v-else class="flex-1 overflow-y-auto p-5">
      <div class="overflow-hidden rounded-lg border">
        <!-- Table header -->
        <div class="grid grid-cols-5 gap-4 border-b bg-surface-gray-1 px-4 py-2 text-xs font-medium uppercase tracking-wide text-ink-gray-5">
          <div class="col-span-2">Subject</div>
          <div>Type</div>
          <div>Status</div>
          <div>Starts On</div>
        </div>

        <!-- Rows -->
        <div
          v-for="event in eventRows"
          :key="event.name"
          class="grid cursor-pointer grid-cols-5 gap-4 border-b px-4 py-3 last:border-b-0 hover:bg-surface-gray-1 transition-colors"
          @click="openEvent(event.name)"
        >
          <div class="col-span-2 font-medium text-ink-gray-9">{{ event.subject }}</div>
          <div class="text-sm text-ink-gray-6">{{ event.event_type || '—' }}</div>
          <div>
            <span
              class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
              :class="statusClass(event.status)"
            >
              {{ event.status }}
            </span>
          </div>
          <div class="text-sm text-ink-gray-6">{{ formatDate(event.starts_on) }}</div>
        </div>
      </div>

      <!-- Pagination info -->
      <div class="mt-3 text-right text-xs text-ink-gray-4">
        Showing {{ eventRows.length }} events
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { createListResource, Button } from 'frappe-ui'
import LucidePresentation from '~icons/lucide/presentation'
import LucideCalendarPlus from '~icons/lucide/calendar-plus'

const router = useRouter()

const events = createListResource({
  doctype: 'Event',
  fields: ['name', 'subject', 'starts_on', 'ends_on', 'status', 'event_type', 'event_category'],
  orderBy: 'starts_on desc',
  pageLength: 50,
  auto: true,
})

const eventRows = computed(() => events.list?.data || [])

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function statusClass(status) {
  const map = {
    Open: 'bg-orange-100 text-orange-700',
    Closed: 'bg-green-100 text-green-700',
    Cancelled: 'bg-red-100 text-red-700',
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

function openEvent(name) {
  router.push({ name: 'Product Demo Event', params: { eventId: name } })
}

function openNewEvent() {
  window.open('/desk/event/new-event-1', '_blank')
}
</script>
