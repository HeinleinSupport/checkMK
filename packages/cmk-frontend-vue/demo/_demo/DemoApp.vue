<!--
Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useRoute } from 'vue-router'

import DemoHeader from './DemoHeader.vue'
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
    <header class="demo-app__header">
      <DemoHeader />
    </header>

    <div class="demo-app__body">
      <aside class="demo-app__sidebar">
        <DemoNavigation />
      </aside>

      <main class="demo-app__main">
        <div class="demo-app__area">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
  <RouterView v-else />
</template>

<style scoped>
.demo-app {
  display: flex;
  flex-direction: column;
  color: var(--font-color);
  background-color: var(--default-bg-color);
  height: 100vh;
  overflow: hidden;
}

.demo-app__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5em 1.5em;
  background-color: var(--default-bg-color);
  border-bottom: 1px solid var(--default-form-element-bg-color);
  height: 50px;
}

.demo-app__body {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 1em;
  gap: 1em;
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
