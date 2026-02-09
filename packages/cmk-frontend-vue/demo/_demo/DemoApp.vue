<!--
Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useRoute } from 'vue-router'

import DemoNavigation from './DemoNavigation.vue'

const currentRoute = useRoute()
const screenshotMode = ref(currentRoute.query.screenshot === 'true')

watch(
  () => currentRoute.query.screenshot,
  (screenshot) => {
    screenshotMode.value = screenshot === 'true'
  }
)
</script>

<template>
  <div v-if="!screenshotMode" class="cmk-vue-app demo-app">
    <div class="demo-app__sidebar">
      <DemoNavigation />
    </div>

    <main class="demo-app__main">
      <h1>{{ currentRoute.meta.name }}</h1>
      <div class="demo-app__area">
        <RouterView />
      </div>
    </main>
  </div>
  <RouterView v-else />
</template>

<style scoped>
.demo-app {
  display: flex;
  color: var(--font-color);
  background-color: var(--default-bg-color);
  height: 100vh;
  gap: 1em;
  padding: 1em;
  overflow: hidden;
}

.demo-app__sidebar {
  display: flex;
  flex-direction: column;
  width: 250px;
  border-right: 1px solid var(--default-form-element-bg-color);
  overflow: hidden auto;
  flex-shrink: 0;
  scrollbar-width: thin;
  scrollbar-color: var(--demo-nav-tree-scroll-bar-color) transparent;
}

.demo-app__sidebar::-webkit-scrollbar {
  width: 6px;
}

.demo-app__sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.demo-app__sidebar::-webkit-scrollbar-thumb {
  background-color: var(--demo-nav-tree-scroll-bar-color);
  border-radius: 20px;
}

.demo-app__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.demo-app__area {
  flex: 1;
  padding: 1em;
  border: 2px solid var(--default-form-element-bg-color);
  background-color: var(--default-component-bg-color);
}
</style>
