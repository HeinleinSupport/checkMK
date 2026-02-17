<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { ref } from 'vue'
import iconUrl from '~cmk-frontend/themes/facelift/images/checkmk_logo.svg'

import DemoGlobalStyles from './DemoGlobalStyles.vue'

const selectedTheme = ref<'facelift' | 'modern-dark'>('facelift')
</script>

<template>
  <div class="demo-header">
    <div class="demo-header__item">
      <img :src="iconUrl" alt="Checkmk logo" width="117" />
    </div>
    <div class="demo-header__item">
      <DemoGlobalStyles v-model:theme="selectedTheme" />
    </div>
  </div>
</template>

<style scoped>
.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.demo-header__item {
  display: flex;
  align-items: center;
}
</style>
