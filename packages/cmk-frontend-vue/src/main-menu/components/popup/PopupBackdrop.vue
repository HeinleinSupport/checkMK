<!--
Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { getInjectedMainMenu } from '@/main-menu/provider/main-menu'

const mainMenu = getInjectedMainMenu()

function backdropClick(e: MouseEvent) {
  if (e.target instanceof HTMLDivElement) {
    if (e.target.classList.contains('mm-popup-backdrop')) {
      mainMenu.close()
    }
  }
}
</script>

<template>
  <div class="mm-popup-backdrop" @click="backdropClick">
    <slot />
  </div>
</template>

<style scoped>
.mm-popup-backdrop {
  backdrop-filter: blur(1.5px);
  position: fixed;
  inset: 0 0 0 64px;
  background: var(--popup-backdrop-color);
}
</style>
