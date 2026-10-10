<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { updateFolderById } from '$lib/apis/folders';

	import {
		config,
		user,
		models as _models,
		temporaryChatEnabled,
		selectedFolder
	} from '$lib/stores';
	import { refreshChatList, refreshFolderChatLists } from '$lib/stores/chatList';
	import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
	import {
		resolveLocalizedModelDescription,
		resolveLocalizedModelName,
		resolveLocalizedModelPromptSuggestions,
		resolveLocalizedPromptSuggestions
	} from '$lib/utils/localizedContent';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

	import Suggestions from './Suggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';
	import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
	import FolderTitle from './Placeholder/FolderTitle.svelte';

	const i18n: any = getContext('i18n');

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];
	export let messageInput = null;

	export let selectedToolIds = [];
	export let selectedSkillIds = [];
	export let selectedFilterIds = [];
	export let pendingOAuthTools = [];

	export let showCommands = false;

	export let imageGenerationEnabled = false;
	export let codeInterpreterEnabled = false;
	export let webSearchEnabled = false;
	export let toolApprovalMode = 'full';
	export let onToolApprovalModeChange: Function = () => {};
	export let oauthRedirectHandler: Function = () => {};

	export let onUpload: Function = (e) => {};
	export let onUpdate: (data?: { file?: any }) => void = () => {};
	export let onSelect = (e) => {};
	export let onChange = (e) => {};
	export let onWebSearchToggle: Function = () => {};
	export let messageQueue: { id: string; prompt: string; files: any[] }[] = [];
	export let onQueueSendNow: (id: string) => void = () => {};
	export let onQueueEdit: (id: string) => void = () => {};
	export let onQueueDelete: (id: string) => void = () => {};
	export let askUser = {
		show: false,
		questions: [],
		allowOther: true,
		timeoutMs: null,
		onConfirm: (_value: any) => {},
		onCancel: () => {}
	};

	export let dragged = false;

	let models = [];
	export let selectedModelIdx = 0;
	let selectedModel;
	let selectedModelName = '';
	let selectedModelDescription = '';
	let selectedSuggestionPrompts = [];

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));
	$: selectedModel = atSelectedModel ?? models[selectedModelIdx];
	$: selectedModelName = resolveLocalizedModelName(selectedModel, $i18n.language);
	$: selectedModelDescription = resolveLocalizedModelDescription(selectedModel, $i18n.language);
	$: selectedSuggestionPrompts =
		resolveLocalizedModelPromptSuggestions(atSelectedModel, $i18n.language) ??
		resolveLocalizedModelPromptSuggestions(models[selectedModelIdx], $i18n.language) ??
		resolveLocalizedPromptSuggestions(
			$config?.default_prompt_suggestions,
			$config?.default_prompt_suggestions_i18n ?? {},
			$i18n.language,
			(key) => $i18n.t(key)
		);

	// True when viewing a shared folder the current user doesn't own AND lacks write access
	$: folderReadOnly =
		$selectedFolder != null &&
		$selectedFolder.user_id !== $user?.id &&
		!$selectedFolder.write_access;
</script>

<div class="m-auto w-full max-w-[58rem] px-1 @2xl:px-20 translate-y-6 py-24 text-center">
	{#if $temporaryChatEnabled}
		<Tooltip
			content={$i18n.t("This chat won't appear in history and your messages will not be saved.")}
			className="w-full flex justify-center mb-0.5"
			placement="top"
		>
			<div class="flex items-center gap-1.5 text-gray-500 text-xs my-1 w-fit">
				<EyeSlash strokeWidth="2" className="size-3.5" />{$i18n.t('Temporary Chat')}
			</div>
		</Tooltip>
	{/if}

	<div class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4">
		<div class="w-full flex flex-col justify-center items-center">
			{#if $selectedFolder}
				<FolderTitle
					folder={$selectedFolder}
					readOnly={folderReadOnly}
					onUpdate={async () => {
						await Promise.all([refreshChatList(localStorage.token), refreshFolderChatLists(null)]);
					}}
					onDelete={async () => {
						await Promise.all([refreshChatList(localStorage.token), refreshFolderChatLists(null)]);

						selectedFolder.set(null);
					}}
				/>
			{:else}
                <div class="flex flex-col items-center gap-4 mb-3">
                    <img src="/static/albe-logo.png" alt="Albe Lestari" class="size-20 rounded-xl object-contain" />
                    <h1 class="text-2xl font-semibold tracking-tight">ALBE BOT</h1>
                </div>
			{/if}

			<div class="text-base font-normal @md:max-w-3xl w-full py-3 {atSelectedModel ? 'mt-2' : ''}">
				{#if !($selectedFolder && folderReadOnly)}
					<MessageInput
						bind:this={messageInput}
						{history}
						bind:selectedModels
						bind:files
						bind:prompt
						bind:autoScroll
						bind:selectedToolIds
						bind:selectedSkillIds
						bind:selectedFilterIds
						bind:imageGenerationEnabled
						bind:codeInterpreterEnabled
						bind:webSearchEnabled
						bind:atSelectedModel
						bind:showCommands
						bind:dragged
						{pendingOAuthTools}
						{oauthRedirectHandler}
						{toolApprovalMode}
						{onToolApprovalModeChange}
						{stopResponse}
						{createMessagePair}
						placeholder={$i18n.t('How can I help you today?')}
						{onChange}
						{onUpload}
						{onUpdate}
						{messageQueue}
						{onQueueSendNow}
						{onQueueEdit}
						{onQueueDelete}
						{askUser}
						{onWebSearchToggle}
						on:chatVariables
						on:submit={(e) => {
							dispatch('submit', e.detail);
						}}
					/>
				{/if}
			</div>
		</div>
	</div>

	{#if $selectedFolder}
		<div class="mx-auto px-4 md:max-w-3xl md:px-6 min-h-62" in:fade={{ duration: 200, delay: 200 }}>
			<FolderPlaceholder folder={$selectedFolder} />
		</div>
	{/if}
</div>
