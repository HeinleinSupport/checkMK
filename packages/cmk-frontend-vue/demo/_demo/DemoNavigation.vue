<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { RouterLink } from 'vue-router'

import DemoNavFolder from './DemoNavFolder.vue'
import { useNavigation } from './useNavigation'

const { navTrees } = useNavigation()
</script>

<template>
  <RouterLink
    to="/"
    class="demo-navigation__home-link"
    active-class="demo-navigation__home-link--active"
  >
    Home
  </RouterLink>

  <template v-for="navTree in navTrees" :key="navTree.path">
    <DemoNavFolder :folder="navTree" :is-root="true" />
  </template>
</template>

<style scoped>
.demo-navigation__home-link {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: var(--demo-nav-tree-parent-item-font-color);
  padding: 8px 0 8px 40px;
  margin-bottom: 4px;
  text-decoration: none;
}

.demo-navigation__home-link--active {
  color: var(--demo-nav-tree-link-active-color);
  border-left: 3px solid var(--demo-nav-tree-link-active-color);
  background-color: var(--demo-nav-tree-link-active-color-bg);
}
</style>
