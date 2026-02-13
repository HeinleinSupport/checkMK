<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import { immediateWatch } from '@/lib/watch'

import CmkDropdown from '@/components/CmkDropdown'

import { type Theme, useTheme } from './useTheme'

const props = defineProps<{
  theme?: Theme
}>()

const { currentTheme, setTheme } = useTheme()

if (props.theme) {
  setTheme(props.theme)
}

const selectedThemeModel = computed({
  get: () => currentTheme.value,
  set: (newTheme: Theme) => setTheme(newTheme)
})

async function setCss() {
  const url = (await import(`~cmk-frontend/themes/${currentTheme.value}/theme.css?url`)).default
  const linkEl = document.getElementById('cmk-theming-stylesheet')
  if (linkEl instanceof HTMLLinkElement) {
    linkEl.href = url
  }
}

function applyThemeToBody(name: Theme) {
  document.body!.dataset['theme'] = name
}

immediateWatch(
  () => currentTheme.value,
  async (name) => {
    await setCss()
    await applyThemeToBody(name as Theme)
  }
)

const themeOptions = [
  { name: 'facelift', title: 'Light Mode' },
  { name: 'modern-dark', title: 'Dark Mode' }
]
</script>

<template>
  <CmkDropdown
    v-model:selected-option="selectedThemeModel"
    :options="{ type: 'fixed', suggestions: themeOptions }"
    label="Theme"
  />
</template>
