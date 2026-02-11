import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { DocumentCreateRequest, TechDocument } from '../types';

type BackendDocumentCategory =
  | 'tutorial'
  | 'design'
  | 'debug_guide'
  | 'learning'
  | 'reference'
  | 'code_generation'
  | 'debug'
  | 'design_decision'
  | 'error_resolution';

interface BackendDocument {
  id: string;
  project_id: string;
  source: string;
  entry_type: BackendDocumentCategory | string;
  summary: string;
  detail: string | null;
  technologies: string[];
  ai_tool: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
}

interface BackendDocumentCreateRequest {
  source?: 'manual' | 'mcp';
  entry_type?: TechDocument['category'];
  summary?: string;
  detail?: string;
  technologies?: string[];
  ai_tool?: string | null;
  metadata?: Record<string, unknown>;
}

const toCategory = (entryType: BackendDocument['entry_type']): TechDocument['category'] => {
  switch (entryType) {
    case 'tutorial':
    case 'design':
    case 'debug_guide':
    case 'learning':
    case 'reference':
      return entryType;
    case 'design_decision':
      return 'design';
    case 'debug':
    case 'error_resolution':
      return 'debug_guide';
    case 'code_generation':
      return 'tutorial';
    default:
      return 'reference';
  }
};

const toSource = (source: string): TechDocument['source'] =>
  source === 'manual' ? 'manual' : 'notion';

const toSourceUrl = (metadata: Record<string, unknown>): string | null => {
  const rawSourceUrl = metadata.source_url;
  if (typeof rawSourceUrl !== 'string') {
    return null;
  }
  const trimmed = rawSourceUrl.trim();
  return trimmed || null;
};

const toTechDocument = (entry: BackendDocument): TechDocument => {
  const metadata = entry.metadata ?? {};
  return {
    id: entry.id,
    project_id: entry.project_id,
    source: toSource(entry.source),
    category: toCategory(entry.entry_type),
    title: entry.summary,
    content: entry.detail,
    technologies: entry.technologies ?? [],
    ai_tool: entry.ai_tool,
    created_at: entry.created_at,
    source_url: toSourceUrl(metadata),
    metadata,
  };
};

const mapSourceToBackend = (source: DocumentCreateRequest['source']): 'manual' | 'mcp' | undefined => {
  if (!source) {
    return undefined;
  }
  return source === 'manual' ? 'manual' : 'mcp';
};

const mergeSourceUrlMetadata = (
  metadata: Record<string, unknown> | undefined,
  sourceUrl: string | undefined
): Record<string, unknown> | undefined => {
  const mergedMetadata = { ...(metadata ?? {}) };
  if (sourceUrl !== undefined) {
    const trimmed = sourceUrl.trim();
    if (trimmed.length > 0) {
      mergedMetadata.source_url = trimmed;
    } else {
      delete mergedMetadata.source_url;
    }
  }
  return Object.keys(mergedMetadata).length > 0 ? mergedMetadata : undefined;
};

const toBackendPayload = (data: Partial<DocumentCreateRequest>): BackendDocumentCreateRequest => {
  const payload: BackendDocumentCreateRequest = {};

  const mappedSource = mapSourceToBackend(data.source);
  if (mappedSource) payload.source = mappedSource;
  if (data.category) payload.entry_type = data.category;
  if (data.title !== undefined) payload.summary = data.title;
  if (data.content !== undefined) payload.detail = data.content;
  if (data.technologies !== undefined) payload.technologies = data.technologies;
  if (data.ai_tool !== undefined) payload.ai_tool = data.ai_tool;

  const mergedMetadata = mergeSourceUrlMetadata(data.metadata, data.source_url);
  if (mergedMetadata) {
    payload.metadata = mergedMetadata;
  }

  return payload;
};

export const getDocuments = async (
  projectId: string
): Promise<{ data: { entries: TechDocument[]; total: number } | null; error: string | null; status?: number }> => {
  const result = await apiGet<{ entries: BackendDocument[]; total: number }>(`/devlogs/${projectId}`);
  if (result.error || !result.data) {
    return { ...result, data: null };
  }

  return {
    ...result,
    data: {
      entries: result.data.entries.map(toTechDocument),
      total: result.data.total,
    },
  };
};

export const createDocument = async (
  projectId: string,
  data: DocumentCreateRequest
): Promise<{ data: TechDocument | null; error: string | null; status?: number }> => {
  const result = await apiPost<BackendDocument, BackendDocumentCreateRequest>(
    `/devlogs/${projectId}/entries`,
    toBackendPayload(data),
  );
  if (result.error || !result.data) {
    return { ...result, data: null };
  }

  return {
    ...result,
    data: toTechDocument(result.data),
  };
};

export const updateDocument = async (
  entryId: string,
  data: Partial<DocumentCreateRequest>
): Promise<{ data: TechDocument | null; error: string | null; status?: number }> => {
  const result = await apiPut<BackendDocument, BackendDocumentCreateRequest>(
    `/devlogs/entries/${entryId}`,
    toBackendPayload(data),
  );
  if (result.error || !result.data) {
    return { ...result, data: null };
  }

  return {
    ...result,
    data: toTechDocument(result.data),
  };
};

export const deleteDocument = (entryId: string) =>
  apiDelete<{ status: string }>(`/devlogs/entries/${entryId}`);
