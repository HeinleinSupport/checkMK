<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { ref } from 'vue'

import { immediateWatch } from '@/lib/watch'

import CmkDropdown from '@/components/CmkDropdown'

const { theme = 'facelift' } = defineProps<{
  theme?: 'facelift' | 'modern-dark'
}>()

const selectedTheme = ref<'facelift' | 'modern-dark'>(theme)

async function setCss() {
  const url = (await import(`~cmk-frontend/themes/${selectedTheme.value}/theme.css?url`)).default
  const linkEl = document.getElementById('cmk-theming-stylesheet')
  if (linkEl instanceof HTMLLinkElement) {
    linkEl.href = url
  }
}

function setTheme(name: 'modern-dark' | 'facelift') {
  document.body!.dataset['theme'] = name
}

immediateWatch(
  () => selectedTheme.value,
  async (name) => {
    await setCss()
    await setTheme(name)
  }
)

const themeOptions = [
  { name: 'facelift', title: 'Light Mode' },
  { name: 'modern-dark', title: 'Dark Mode' }
]
</script>

<template>
  <CmkDropdown
    v-model:selected-option="selectedTheme"
    :options="{ type: 'fixed', suggestions: themeOptions }"
    label="Theme"
  />
</template>
