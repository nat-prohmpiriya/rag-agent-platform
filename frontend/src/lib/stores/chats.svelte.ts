import { conversationsApi, type Conversation } from '$lib/api';

const PER_PAGE = 20;

class ChatStore {
	conversations = $state<Conversation[]>([]);
	loading = $state(false);
	loadingMore = $state(false);
	currentPage = $state(1);
	hasMore = $state(true);
	initialized = $state(false);
	currentId = $state<string | null>(null);

	async loadInitial() {
		if (this.loading) return;

		this.loading = true;
		this.currentPage = 1;

		try {
			const response = await conversationsApi.list(1, PER_PAGE);
			this.conversations = response.items;
			this.hasMore = response.items.length === PER_PAGE && response.page < response.pages;
			this.initialized = true;
		} catch (e) {
			console.error('Failed to load conversations:', e);
		} finally {
			this.loading = false;
		}
	}

	async loadMore() {
		if (this.loadingMore || !this.hasMore) return;

		this.loadingMore = true;
		const nextPage = this.currentPage + 1;

		try {
			const response = await conversationsApi.list(nextPage, PER_PAGE);
			this.conversations = [...this.conversations, ...response.items];
			this.currentPage = nextPage;
			this.hasMore = response.items.length === PER_PAGE && response.page < response.pages;
		} catch (e) {
			console.error('Failed to load more conversations:', e);
		} finally {
			this.loadingMore = false;
		}
	}

	async delete(id: string) {
		try {
			await conversationsApi.delete(id);
			this.conversations = this.conversations.filter((c) => c.id !== id);
		} catch (e) {
			console.error('Failed to delete conversation:', e);
			throw e;
		}
	}

	addConversation(conv: Conversation) {
		// Add to the beginning
		this.conversations = [conv, ...this.conversations];
	}

	updateConversation(id: string, updates: Partial<Conversation>) {
		this.conversations = this.conversations.map((c) =>
			c.id === id ? { ...c, ...updates } : c
		);
	}

	setCurrentId(id: string | null) {
		this.currentId = id;
	}

	clear() {
		this.conversations = [];
		this.loading = false;
		this.loadingMore = false;
		this.currentPage = 1;
		this.hasMore = true;
		this.initialized = false;
		this.currentId = null;
	}
}

export const chatStore = new ChatStore();
