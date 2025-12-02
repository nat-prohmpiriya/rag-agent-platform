import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { marked } from 'marked';
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import python from 'highlight.js/lib/languages/python';
import sql from 'highlight.js/lib/languages/sql';
import json from 'highlight.js/lib/languages/json';
import bash from 'highlight.js/lib/languages/bash';
import xml from 'highlight.js/lib/languages/xml';
import css from 'highlight.js/lib/languages/css';

// Register languages
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('js', javascript);
hljs.registerLanguage('typescript', typescript);
hljs.registerLanguage('ts', typescript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('py', python);
hljs.registerLanguage('sql', sql);
hljs.registerLanguage('json', json);
hljs.registerLanguage('bash', bash);
hljs.registerLanguage('sh', bash);
hljs.registerLanguage('shell', bash);
hljs.registerLanguage('html', xml);
hljs.registerLanguage('xml', xml);
hljs.registerLanguage('css', css);

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// Custom renderer for code blocks with syntax highlighting
const renderer = new marked.Renderer();

renderer.code = ({ text, lang }: { text: string; lang?: string }) => {
	const language = lang || 'plaintext';
	let highlighted: string;

	try {
		if (hljs.getLanguage(language)) {
			highlighted = hljs.highlight(text, { language }).value;
		} else {
			highlighted = hljs.highlightAuto(text).value;
		}
	} catch {
		highlighted = text;
	}

	const escapedLang = language.replace(/"/g, '&quot;');
	return `<div class="code-block-wrapper relative group">
		<div class="code-block-header flex items-center justify-between px-4 py-2 bg-slate-800 text-slate-400 text-xs rounded-t-lg border-b border-slate-700">
			<span>${escapedLang}</span>
			<button class="copy-btn opacity-0 group-hover:opacity-100 transition-opacity hover:text-white" onclick="navigator.clipboard.writeText(this.closest('.code-block-wrapper').querySelector('code').textContent).then(() => { this.textContent = 'Copied!'; setTimeout(() => this.textContent = 'Copy', 2000); })">Copy</button>
		</div>
		<pre class="mt-0! rounded-t-none!"><code class="hljs language-${escapedLang}">${highlighted}</code></pre>
	</div>`;
};

// Configure marked for safe rendering
marked.setOptions({
	gfm: true, // GitHub Flavored Markdown
	breaks: true, // Convert \n to <br>
	renderer,
});

/**
 * Parse markdown to HTML with syntax highlighting
 */
export function parseMarkdown(content: string): string {
	if (!content) return '';

	try {
		return marked.parse(content, { async: false }) as string;
	} catch (e) {
		console.error('Markdown parse error:', e);
		return content;
	}
}

/**
 * Simple code block detection for syntax highlighting
 */
export function extractCodeBlocks(content: string): { language: string; code: string }[] {
	const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
	const blocks: { language: string; code: string }[] = [];

	let match;
	while ((match = codeBlockRegex.exec(content)) !== null) {
		blocks.push({
			language: match[1] || 'text',
			code: match[2].trim(),
		});
	}

	return blocks;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChild<T> = T extends { child?: any } ? Omit<T, "child"> : T;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, "children"> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };
