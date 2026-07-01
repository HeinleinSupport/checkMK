<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import usei18n from '@/lib/i18n'

import CmkAlertBox from '@/components/CmkAlertBox.vue'

const { _t } = usei18n()
</script>

<template>
  <CmkAlertBox
    variant="info"
    :heading="_t('Microsoft Entra ID connections are only used by email checks')"
  >
    {{
      _t(
        'A connection configured here only creates an OAuth2 token that the Check email, Check email delivery and Check mailboxes active checks use to authenticate against Microsoft 365 mailboxes. It is not a general-purpose identity provider or single sign-on connection.'
      )
    }}
  </CmkAlertBox>
</template>
