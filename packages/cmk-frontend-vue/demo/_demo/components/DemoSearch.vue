<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import CmkIcon from '@/components/CmkIcon'

import { type NavItem, type NavPage, useNavigation } from '../composables/useNavigation'
import DemoNavPage from './DemoNavPage.vue'

const { navTrees } = useNavigation()

const isSearching = defineModel<boolean>('isSearching', { default: false })

const searchQuery = ref('')

function clearSearch() {
  searchQuery.value = ''
}

function collectPages(items: NavItem[]): NavPage[] {
  const pages: NavPage[] = []
  for (const item of items) {
    if (item.type === 'page') {
      pages.push(item)
    } else {
      pages.push(...collectPages(item.children))
    }
  }
  return pages
}

const allPages = navTrees.flatMap((tree) => collectPages(tree.children))

const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return q ? allPages.filter((p) => p.name.toLowerCase().includes(q)) : null
})

watch(searchResults, (results) => {
  isSearching.value = results !== null
})
</script>

<template>
  <div class="demo-search__input-wrapper">
    <div class="demo-search__input-root">
      <CmkIcon class="demo-search__input-icon" name="main-search" size="small" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search..."
        class="demo-search__input-field"
      />
    </div>
    <CmkIcon
      v-if="searchQuery.length > 0"
      class="demo-search__input-reset"
      name="close"
      size="small"
      @click.stop="clearSearch"
    />
  </div>

  <ul v-if="searchResults" class="demo-search__results">
    <li v-for="page in searchResults" :key="page.path">
      <DemoNavPage :page="page" />
    </li>
    <li v-if="searchResults.length === 0">No results found</li>
  </ul>
</template>

<style scoped>
.demo-search__input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 95%;
  position: relative;
  margin-bottom: 12px;
}

.demo-search__input-root {
  background-color: var(--default-form-element-bg-color);
  padding: 0 35px 0 0;
  width: 100%;
  border-radius: 2px;
  border: 1px solid var(--default-form-element-border-color);
  height: 24px;
  display: flex;
  align-items: center;

  &:focus-within {
    border: 1px solid var(--success);
  }
}

.demo-search__input-icon {
  margin-left: var(--dimension-4, 8px);
  opacity: 0.6;
}

.demo-search__input-field {
  background: transparent;
  border: 0;
  width: 100%;
  height: 24px;
  padding: 0;
  margin-left: var(--dimension-4, 8px);
  color: var(--font-color);

  &::placeholder {
    color: var(--default-form-element-placeholder-color);
  }

  &:focus {
    outline: none;
  }
}

.demo-search__input-reset {
  opacity: 0.6;
  cursor: pointer;
  position: absolute;
  right: 8px;

  &:hover {
    opacity: 1;
  }
}

.demo-search__results {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
