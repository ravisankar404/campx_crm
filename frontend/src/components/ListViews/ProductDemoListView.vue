<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      getRowRoute: (row) => ({
        name: 'Product Demo Event',
        params: { eventId: row.name },
      }),
      showTooltip: false,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
  >
    <ListHeader
      class="sm:mx-5 mx-3"
      @columnWidthUpdated="emit('columnWidthUpdated')"
    >
      <ListHeaderItem
        v-for="column in columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      />
    </ListHeader>
    <ListRows v-slot="{ column, item }" :rows="rows" doctype="Event">
      <ListRowItem :item="item" :align="column.align">
        <template #default="{ label }">
          <div
            v-if="column.key === '_attendees'"
            class="flex flex-wrap gap-1"
          >
            <span
              v-for="a in (Array.isArray(item) ? item.slice(0, 3) : [])"
              :key="a"
              class="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
            >{{ a }}</span>
            <span
              v-if="Array.isArray(item) && item.length > 3"
              class="text-xs text-ink-gray-4"
            >
              +{{ item.length - 3 }} more
            </span>
            <span v-else-if="!Array.isArray(item) || !item.length" class="text-xs text-ink-gray-3">—</span>
          </div>
          <Badge
            v-else-if="column.key === 'status' && item?.label"
            :label="item.label"
            :theme="item.color"
            variant="subtle"
            size="md"
          />
          <div
            v-else-if="column.key === '_orgName'"
            class="flex items-center gap-1 truncate text-base"
          >
            <LucideBuilding2
              v-if="item?.label"
              class="h-3 w-3 shrink-0 text-ink-gray-4"
            />
            <span v-if="item?.label" class="truncate text-ink-gray-7">{{ item.label }}</span>
            <span v-else class="text-ink-gray-3">—</span>
          </div>
          <Tooltip
            v-else-if="
              ['starts_on', 'ends_on', 'modified', 'creation'].includes(column.key) && item?.label
            "
            :text="item.label"
          >
            <div class="truncate text-base">{{ item.timeAgo || item.label }}</div>
          </Tooltip>
          <div v-else-if="label" class="truncate text-base">{{ label }}</div>
        </template>
      </ListRowItem>
    </ListRows>
    <ListFooter
      v-if="pageLengthCount"
      v-model="pageLengthCount"
      class="border-t sm:px-5 px-3 py-2"
      :options="{
        rowCount: options.rowCount,
        totalCount: options.totalCount,
      }"
      @loadMore="emit('loadMore')"
    />
  </ListView>
</template>

<script setup>
import ListRows from '@/components/ListViews/ListRows.vue'
import LucideBuilding2 from '~icons/lucide/building-2'
import {
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRowItem,
  ListFooter,
  Tooltip,
  Badge,
} from 'frappe-ui'

const pageLengthCount = defineModel({ type: Number })

defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  options: {
    type: Object,
    default: () => ({
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})

const emit = defineEmits(['loadMore', 'columnWidthUpdated', 'updatePageCount'])
</script>
