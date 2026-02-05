<!--
Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useRoute } from 'vue-router'

import { immediateWatch } from '@/lib/watch'

import CmkButton from '@/components/CmkButton.vue'
import CmkToggleButtonGroup from '@/components/CmkToggleButtonGroup.vue'

import DemoNavigation from './DemoNavigation.vue'
import router from './router'

const selectedTheme = ref<'facelift' | 'modern-dark'>('facelift')
const selectedCss = ref<'cmk' | 'none'>('cmk')

const currentRoute = useRoute()
const screenshotMode = ref(currentRoute.query.screenshot === 'true')

async function enableScreenshotMode() {
  await router.push({ path: currentRoute.path, query: { screenshot: 'true' } })
}

watch(
  () => currentRoute.query.screenshot,
  (screenshot) => {
    screenshotMode.value = screenshot === 'true'
  }
)

async function setTheme(name: 'modern-dark' | 'facelift') {
  document.getElementsByTagName('body')[0]!.dataset['theme'] = name
}

async function setCss(name: 'cmk' | 'none') {
  let url: string
  if (name === 'none') {
    url = ''
  } else {
    url = (await import(`~cmk-frontend/themes/${selectedTheme.value}/theme.css?url`)).default
  }
  ;(document.getElementById('cmk-theming-stylesheet') as HTMLLinkElement).href = url
}

immediateWatch(
  () => selectedCss.value,
  async (name: 'cmk' | 'none') => {
    selectedCss.value = name
    await setCss(name)
    await setTheme(selectedTheme.value)
  }
)

immediateWatch(
  () => selectedTheme.value,
  async (name: 'facelift' | 'modern-dark') => {
    selectedTheme.value = name
    await setCss(selectedCss.value)
    await setTheme(name)
  }
)
</script>

<template>
  <div v-if="!screenshotMode" class="cmk-vue-app demo-app">
    <div class="demo-app__sidebar">
      <div class="demo-app__controls">
        <fieldset>
          <legend>global styles</legend>
          <CmkToggleButtonGroup
            v-model="selectedCss"
            :options="[
              { label: 'cmk', value: 'cmk' },
              { label: 'none', value: 'none' }
            ]"
          />
          <CmkToggleButtonGroup
            v-model="selectedTheme"
            :options="[
              { label: 'light', value: 'facelift' },
              { label: 'dark', value: 'modern-dark' }
            ]"
          />
          <CmkButton @click="enableScreenshotMode">screenshot mode</CmkButton>
        </fieldset>
      </div>
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
