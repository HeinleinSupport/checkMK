<!--
Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import usei18n from '@/lib/i18n'
import WelcomeBanner from './components/WelcomeBanner.vue'
import WelcomeFooter from './components/WelcomeFooter.vue'

const { t } = usei18n('welcome-app')
</script>

<template>
  <div class="welcome-app">
    <WelcomeBanner :completed-steps="1" :total-steps="5" />
    <p>
      {{
        t(
          'placeholder',
          'This is just a placeholder for the Welcome page. It will be used to guide you through the first steps of using Checkmk.'
        )
      }}
    </p>
    <p>
      {{
        t(
          'change-start-url',
          'In case you want to change the start URL to the main dashboard, you can do so under User > Edit profile > Start URL.'
        )
      }}
    </p>

    <WelcomeFooter class="welcome-app__footer" />
  </div>
</template>

<style scoped>
.welcome-app {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 20px);
}

.welcome-app__footer {
  margin-top: auto;
}
</style>
