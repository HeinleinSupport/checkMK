<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import CmkButton from '@/components/CmkButton.vue'

import ctaBackgroundImageModernDark from './assets/images/cta-banner-bg-dark.png'
import ctaBackgroundImageFacelift from './assets/images/cta-banner-bg-light.png'
import { useTheme } from './useTheme'

const props = defineProps<{
  title: string
  subtitle?: string
  buttonText: string
  buttonUrl: string
}>()

const { getByTheme } = useTheme()

const ctaBackgroundImage = computed(() => {
  return getByTheme(ctaBackgroundImageFacelift, ctaBackgroundImageModernDark)
})

const handleButtonClick = () => {
  window.open(props.buttonUrl, '_blank', 'noopener,noreferrer')
}
</script>

<template>
  <div class="demo-cta-banner" :style="{ backgroundImage: `url(${ctaBackgroundImage})` }">
    <div class="demo-cta-banner__content">
      <h2 class="demo-cta-banner__title">{{ title }}</h2>
      <p class="demo-cta-banner__subtitle">{{ subtitle }}</p>
      <CmkButton variant="primary" @click="handleButtonClick">
        {{ buttonText }}
      </CmkButton>
    </div>
  </div>
</template>

<style scoped>
.demo-cta-banner {
  background-size: contain;
  background-position: left center;
  background-repeat: no-repeat;
  background-color: var(--demo-elements-background-color);
  border-radius: 4px;
  padding: 40px 40px 40px 200px;
  display: flex;
  align-items: center;
  min-height: 200px;
}

.demo-cta-banner__content {
  position: relative;
  max-width: 700px;
}

.demo-cta-banner__title {
  color: var(--demo-cta-banner-title-color);
  font-size: 24px;
  font-style: normal;
  font-weight: 700;
  line-height: normal;
  margin: 0 0 12px;
}

.demo-cta-banner__subtitle {
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;
  margin: 0 0 24px;
}
</style>
