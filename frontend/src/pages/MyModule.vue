<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between border-b px-5 py-3">
      <h1 class="text-xl font-semibold text-ink-gray-9">My Module</h1>
      <Button label="New Record" variant="solid" @click="showForm = !showForm" />
    </div>

    <!-- Custom Form (toggle) -->
    <div v-if="showForm" class="border-b bg-surface-gray-1 px-5 py-4">
      <div class="flex gap-4">
        <FormControl
          v-model="newRecord.title"
          label="Title"
          placeholder="Enter title"
          class="flex-1"
        />
        <FormControl
          v-model="newRecord.description"
          label="Description"
          placeholder="Enter description"
          class="flex-1"
        />
        <div class="flex items-end gap-2">
          <Button label="Add" variant="solid" @click="addRecord" />
          <Button label="Cancel" @click="showForm = false" />
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-5">
      <!-- Empty state -->
      <div
        v-if="records.length === 0"
        class="flex h-full flex-col items-center justify-center gap-3 text-ink-gray-5"
      >
        <LucideFlaskConical class="h-16 w-16 opacity-30" />
        <p class="text-lg font-medium">No records yet</p>
        <p class="text-sm">Click "New Record" to add your first entry.</p>
      </div>

      <!-- Records list -->
      <div v-else class="space-y-3">
        <div
          v-for="(record, index) in records"
          :key="index"
          class="flex items-start justify-between rounded-lg border bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
        >
          <div>
            <p class="font-semibold text-ink-gray-9">{{ record.title }}</p>
            <p class="mt-1 text-sm text-ink-gray-5">{{ record.description }}</p>
            <p class="mt-2 text-xs text-ink-gray-4">Added: {{ record.date }}</p>
          </div>
          <Button
            variant="ghost"
            icon="x"
            @click="removeRecord(index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FormControl } from 'frappe-ui'
import LucideFlaskConical from '~icons/lucide/flask-conical'

const showForm = ref(false)

const newRecord = ref({
  title: '',
  description: '',
})

const records = ref([])

function addRecord() {
  if (!newRecord.value.title.trim()) return
  records.value.push({
    title: newRecord.value.title,
    description: newRecord.value.description,
    date: new Date().toLocaleString(),
  })
  newRecord.value = { title: '', description: '' }
  showForm.value = false
}

function removeRecord(index) {
  records.value.splice(index, 1)
}
</script>
