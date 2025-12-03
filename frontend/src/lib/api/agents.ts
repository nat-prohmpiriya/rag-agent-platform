import { fetchApi } from './client';

export interface AgentInfo {
	name: string;
	slug: string;
	icon?: string;
	description?: string;
	tools: string[];
	settings?: Record<string, unknown>;
	privacy?: Record<string, unknown>;
}

export interface AgentDetail extends AgentInfo {
	system_prompt?: string;
}

export interface ToolInfo {
	name: string;
	description: string;
}

export interface AgentListResponse {
	agents: AgentInfo[];
	total: number;
}

export interface AgentToolsResponse {
	agent_slug: string;
	tools: ToolInfo[];
}

export const agentsApi = {
	/**
	 * List all available agents
	 */
	list: async (): Promise<AgentListResponse> => {
		return fetchApi<AgentListResponse>('/api/agents', {
			method: 'GET',
		});
	},

	/**
	 * Get agent detail by slug
	 */
	get: async (slug: string): Promise<AgentDetail> => {
		return fetchApi<AgentDetail>(`/api/agents/${slug}`, {
			method: 'GET',
		});
	},

	/**
	 * Get tools available for an agent
	 */
	getTools: async (slug: string): Promise<AgentToolsResponse> => {
		return fetchApi<AgentToolsResponse>(`/api/agents/${slug}/tools`, {
			method: 'GET',
		});
	},
};
