<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center gap-3 border-b px-5 py-3">
      <Button variant="ghost" @click="goBack">
        <template #prefix>
          <LucideArrowLeft class="h-4 w-4" />
        </template>
        Product Demo
      </Button>
      <span class="text-ink-gray-4">/</span>
      <span class="font-medium text-ink-gray-9">{{ event?.subject || eventId }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-ink-gray-5">Loading event...</div>
    </div>

    <!-- Event Detail -->
    <div v-else-if="event" class="flex-1 overflow-y-auto">
      <div class="mx-auto max-w-4xl p-6">
        <!-- Title card -->
        <div class="mb-6 rounded-xl border bg-white p-6 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <h2 class="text-2xl font-bold text-ink-gray-9">{{ event.subject }}</h2>
              <p class="mt-1 text-sm text-ink-gray-5">{{ event.name }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="rounded-full px-3 py-1 text-sm font-medium"
                :class="statusClass(event.status)"
              >
                {{ event.status }}
              </span>
              <Button
                label="Open in Desk"
                variant="outline"
                @click="openInDesk"
              >
                <template #prefix>
                  <LucideExternalLink class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </div>
        </div>

        <!-- Details grid -->
        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">Schedule</h3>
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
                <span class="text-sm text-ink-gray-5">All Day</span>
                <span class="text-sm font-medium text-ink-gray-9">{{ event.all_day ? 'Yes' : 'No' }}</span>
              </div>
            </div>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">Details</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-ink-gray-5">Event Type</span>
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
            </div>
          </div>

          <!-- Description -->
          <div v-if="event.description" class="col-span-2 rounded-xl border bg-white p-5 shadow-sm">
            <h3 class="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-gray-5">Description</h3>
            <div class="prose prose-sm max-w-none text-ink-gray-7" v-html="event.description" />
          </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideExternalLink from '~icons/lucide/external-link'
import LucidePresentation from '~icons/lucide/presentation'

const props = defineProps({ eventId: String })
const router = useRouter()
const event = ref(null)
const loading = ref(true)

const eventResource = createResource({
  url: 'frappe.client.get',
  params: { doctype: 'Event', name: props.eventId },
  onSuccess(data) {
    event.value = data
    loading.value = false
  },
  onError() {
    loading.value = false
  },
})

onMounted(() => eventResource.fetch())

function goBack() {
  router.push({ name: 'Product Demo' })
}

function openInDesk() {
  window.open(`/desk/event/${props.eventId}`, '_blank')
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
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
</script>
