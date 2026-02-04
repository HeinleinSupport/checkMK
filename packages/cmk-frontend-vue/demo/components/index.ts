/**
 * Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import DemoEmpty from '@demo/_demo/DemoEmpty.vue'
import { Folder, Page } from '@demo/_demo/page'

import DemoCmkBadge from './basic-elements/DemoCmkBadge.vue'
import DemoCmkButton from './basic-elements/DemoCmkButton.vue'
import DemoCmkChip from './basic-elements/DemoCmkChip.vue'
import DemoCmkCode from './basic-elements/DemoCmkCode.vue'
import DemoCmkColorPicker from './basic-elements/DemoCmkColorPicker.vue'
import DemoCmkSwitch from './basic-elements/DemoCmkSwitch.vue'
import { pages as CmkAccordionPages } from './content-organization/CmkAccordion'
import DemoCmkSlideInDialog from './content-organization/CmkAccordion/DemoCmkSlideInDialog.vue'
import { pages as CmkAccordionStepPanelPages } from './content-organization/CmkAccordionStepPanel'
import { pages as CmkTabPages } from './content-organization/CmkTabs'
import DemoCmkWizard from './content-organization/CmkWizard/DemoCmkWizard.vue'
import DemoCmkCatalogPanel from './content-organization/DemoCmkCatalogPanel.vue'
import DemoCmkCollapsible from './content-organization/DemoCmkCollapsible.vue'
import DemoCmkScrollContainer from './content-organization/DemoCmkScrollContainer.vue'
import DemoCmkSlideIn from './content-organization/DemoCmkSlideIn.vue'
import DemoTwoFactorAuth from './content-organization/DemoTwoFactorAuthentication.vue'
import { pages as formElementPages } from './form-elements'
import DemoCmkCheckbox from './form-elements/DemoCmkCheckbox.vue'
import DemoCmkDropdown from './form-elements/DemoCmkDropdown.vue'
import DemoCmkDualList from './form-elements/DemoCmkDualList.vue'
import DemoCmkInput from './form-elements/DemoCmkInput.vue'
import DemoCmkList from './form-elements/DemoCmkList.vue'
import DemoCmkToggleButtonGroup from './form-elements/DemoCmkToggleButtonGroup.vue'
import { pages as CmkIconPages } from './foundation-elements/CmkIcon'
import DemoCmkHtml from './foundation-elements/DemoCmkHtml.vue'
import DemoCmkIndent from './foundation-elements/DemoCmkIndent.vue'
import DemoCmkKeyboardKey from './foundation-elements/DemoCmkKeyboardKey.vue'
import DemoCmkLabelRequired from './foundation-elements/DemoCmkLabelRequired.vue'
import DemoCmkSpace from './foundation-elements/DemoCmkSpace.vue'
import DemoCmkZebra from './foundation-elements/DemoCmkZebra.vue'
import { pages as typographyPages } from './foundation-elements/typography'
import DemoCmkLinkCard from './navigation/DemoCmkLinkCard.vue'
import DemoCmkAlertBox from './system-feedback/DemoCmkAlertBox.vue'
import DemoCmkDialog from './system-feedback/DemoCmkDialog.vue'
import DemoCmkInlineValidation from './system-feedback/DemoCmkInlineValidation.vue'
import DemoCmkLoading from './system-feedback/DemoCmkLoading.vue'
import DemoCmkPerfometer from './system-feedback/DemoCmkPerfometer.vue'
import DemoCmkPopupDialog from './system-feedback/DemoCmkPopupDialog.vue'
import DemoCmkProgressbar from './system-feedback/DemoCmkProgressbar.vue'
import DemoCmkSkeleton from './system-feedback/DemoCmkSkeleton.vue'
import DemoCmkTooltip from './system-feedback/DemoCmkTooltip.vue'
import DemoErrorBoundary from './system-feedback/DemoErrorBoundary.vue'
import DemoHelp from './system-feedback/DemoHelp.vue'

const basicElementsPages = [
  new Page('CmkBadge', DemoCmkBadge),
  new Page('CmkButton', DemoCmkButton),
  new Page('CmkChip', DemoCmkChip),
  new Page('CmkCode', DemoCmkCode),
  new Page('CmkColorPicker', DemoCmkColorPicker),
  new Page('CmkSwitch', DemoCmkSwitch)
]

const contentOrganizationPages = [
  new Folder('CmkAccordion', DemoEmpty, CmkAccordionPages),
  new Folder('CmkAccordionStepPanel', DemoEmpty, CmkAccordionStepPanelPages),
  new Folder('CmkTabs', DemoEmpty, CmkTabPages),
  new Page('CmkCatalogPanel', DemoCmkCatalogPanel),
  new Page('CmkCollapsible', DemoCmkCollapsible),
  new Page('CmkScrollContainer', DemoCmkScrollContainer),
  new Page('CmkSlideIn', DemoCmkSlideIn),
  new Page('CmkSlideInDialog', DemoCmkSlideInDialog),
  new Page('CmkWizard', DemoCmkWizard),
  new Page('TwoFactorAuth', DemoTwoFactorAuth)
]

const formElementsPages = [
  new Folder('FormSpec', DemoEmpty, formElementPages),
  new Page('CmkCheckbox', DemoCmkCheckbox),
  new Page('CmkDropdown', DemoCmkDropdown),
  new Page('CmkDualList', DemoCmkDualList),
  new Page('CmkInput', DemoCmkInput),
  new Page('CmkList', DemoCmkList),
  new Page('CmkToggleButtonGroup', DemoCmkToggleButtonGroup)
]

const foundationElementsPages = [
  new Folder('CmkIcons', DemoEmpty, CmkIconPages),
  new Folder('typography', DemoEmpty, typographyPages),
  new Page('CmkHtml', DemoCmkHtml),
  new Page('CmkIndent', DemoCmkIndent),
  new Page('CmkKeyboardKey', DemoCmkKeyboardKey),
  new Page('CmkLabelRequired', DemoCmkLabelRequired),
  new Page('CmkSpace', DemoCmkSpace),
  new Page('CmkZebra', DemoCmkZebra)
]

const navigationPages = [new Page('CmkLinkCard', DemoCmkLinkCard)]

const systemFeedbackPages = [
  new Page('CmkAlertBox', DemoCmkAlertBox),
  new Page('CmkDialog', DemoCmkDialog),
  new Page('CmkErrorBoundary', DemoErrorBoundary),
  new Page('CmkHelpText', DemoHelp),
  new Page('CmkInlineValidation', DemoCmkInlineValidation),
  new Page('CmkLoading', DemoCmkLoading),
  new Page('CmkPerfometer', DemoCmkPerfometer),
  new Page('CmkPopupDialog', DemoCmkPopupDialog),
  new Page('CmkProgressbar', DemoCmkProgressbar),
  new Page('CmkSkeleton', DemoCmkSkeleton),
  new Page('CmkTooltip', DemoCmkTooltip)
]

export const pages = [
  new Folder('basic-elements', DemoEmpty, basicElementsPages),
  new Folder('content-organization', DemoEmpty, contentOrganizationPages),
  new Folder('form-elements', DemoEmpty, formElementsPages),
  new Folder('foundation-elements', DemoEmpty, foundationElementsPages),
  new Folder('navigation', DemoEmpty, navigationPages),
  new Folder('system-feedback', DemoEmpty, systemFeedbackPages)
]
