<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { RouterLink } from 'vue-router'

import type { NavPage } from './useNavigation'

const { page } = defineProps<{
  page: NavPage
}>()
</script>

<template>
  <RouterLink
    :to="page.path"
    class="demo-nav-page"
    active-class="demo-nav-page--active"
    exact-active-class="demo-nav-page--active"
  >
    {{ page.name }}
  </RouterLink>
</template>

<style scoped>
.demo-nav-page {
  display: block;
  padding: 6px 0 6px 20px;
  text-decoration: none;
  cursor: pointer;
}

.demo-nav-page--active {
  color: var(--demo-nav-tree-link-active-color);
  font-weight: 700;
  border-left: 3px solid var(--demo-nav-tree-link-active-color);
  background-color: var(--demo-nav-tree-link-active-color-bg);
  padding: 6px 0 6px 17px;
}
</style>
