<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { TranslatedString } from '@/lib/i18nString'

import CmkIcon from '@/components/CmkIcon'
import type { SimpleIcons } from '@/components/CmkIcon'
import CmkHeading from '@/components/typography/CmkHeading.vue'
import CmkParagraph from '@/components/typography/CmkParagraph.vue'

interface DemoInfoCardProps {
  iconName?: SimpleIcons | undefined
  title: TranslatedString
  subtitle?: TranslatedString
  bulletPoints?: TranslatedString[]
}

const { iconName, title, subtitle, bulletPoints = [] } = defineProps<DemoInfoCardProps>()
</script>

<template>
  <div class="demo-info-card">
    <div class="demo-info-card__header">
      <CmkIcon v-if="iconName" :name="iconName" size="large" class="demo-info-card__header-icon" />
      <CmkHeading type="h4" class="demo-info-card__heading">{{ title }}</CmkHeading>
    </div>

    <div class="demo-info-card__content">
      <CmkParagraph v-if="subtitle" class="demo-info-card__subtitle">
        {{ subtitle }}
      </CmkParagraph>

      <ul v-if="bulletPoints.length" class="demo-info-card__list">
        <li v-for="(point, index) in bulletPoints" :key="index" class="demo-info-card__list-item">
          {{ point }}
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.demo-info-card {
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  padding: var(--dimension-6);
  gap: var(--dimension-5);
  background-color: var(--demo-elements-background-color);
}

.demo-info-card__header {
  display: flex;
  align-items: center;
  gap: var(--dimension-4);
  justify-content: center;
}

.demo-info-card__header-icon {
  flex-shrink: 0;
  color: var(--font-color-base);
}

.demo-info-card__subtitle {
  color: var(--font-color-dimmed);
  margin-bottom: var(--dimension-4);
}

.demo-info-card__list {
  margin: 0;
  padding-left: var(--dimension-8);
  list-style-type: disc;
}

.demo-info-card__list-item {
  color: var(--font-color-base);
  line-height: 1.6;
  margin-bottom: var(--dimension-3);
}

.demo-info-card__list-item:last-child {
  margin-bottom: 0;
}
</style>
