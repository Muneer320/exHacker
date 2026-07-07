"use client";

import React, { createContext, useContext, useReducer, useCallback, useRef } from "react";
import type { PipelineState, PipelineAction, StreamingLogEntry } from "./types";
import { createInitialState, PIPELINE_STAGES } from "./types";

// ─── Reducer ──────────────────────────────────────────────────────────────────

function pipelineReducer(state: PipelineState, action: PipelineAction): PipelineState {
  switch (action.type) {
    case "SET_STAGE_STATUS": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: {
          ...state.stages,
          [action.stageId]: { ...stage, status: action.status, lastUpdated: Date.now() },
        },
      };
    }
    case "SET_PROGRESS": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, progress: action.progress } },
      };
    }
    case "SET_CONFIDENCE": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, confidence: action.confidence } },
      };
    }
    case "SET_MODEL": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, modelUsed: action.model } },
      };
    }
    case "SET_RUNTIME": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, runtime: action.runtime } },
      };
    }
    case "SET_SUMMARY": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, summary: action.summary } },
      };
    }
    case "SET_KEY_FINDINGS": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, keyFindings: action.findings } },
      };
    }
    case "SET_ERROR": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: { ...state.stages, [action.stageId]: { ...stage, error: action.error, status: "failed" } },
      };
    }
    case "TOGGLE_EXPAND": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: {
          ...state.stages,
          [action.stageId]: { ...stage, expanded: !stage.expanded },
        },
      };
    }
    case "ADD_LOG": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return {
        ...state,
        stages: {
          ...state.stages,
          [action.stageId]: { ...stage, log: [...stage.log, action.entry] },
        },
      };
    }
    case "CLEAR_LOG": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return { ...state, stages: { ...state.stages, [action.stageId]: { ...stage, log: [] } } };
    }
    case "MARK_CACHED": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return { ...state, stages: { ...state.stages, [action.stageId]: { ...stage, isCached: action.isCached } } };
    }
    case "MARK_FALLBACK": {
      const stage = state.stages[action.stageId];
      if (!stage) return state;
      return { ...state, stages: { ...state.stages, [action.stageId]: { ...stage, isFallback: action.isFallback } } };
    }
    case "SET_ACTIVE_STAGE":
      return { ...state, activeStageId: action.stageId };
    case "RESET":
      return createInitialState(state.projectName);
    default:
      return state;
  }
}

// ─── Context ──────────────────────────────────────────────────────────────────

interface PipelineContextType {
  state: PipelineState;
  dispatch: React.Dispatch<PipelineAction>;
  /** Start a specialist — animate running → streaming → completed */
  runStage: (stageId: string, config?: {
    model?: string;
    confidence?: number;
    summary?: string;
    findings?: string[];
    isCached?: boolean;
    isFallback?: boolean;
    simulateLog?: boolean;
  }) => Promise<void>;
  /** Get the stage definition for a stage ID */
  getDefinition: (stageId: string) => (typeof PIPELINE_STAGES)[number] | undefined;
}

const PipelineContext = createContext<PipelineContextType | null>(null);

export function usePipeline(): PipelineContextType {
  const ctx = useContext(PipelineContext);
  if (!ctx) throw new Error("usePipeline must be used within PipelineProvider");
  return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function PipelineProvider({
  children,
  projectName,
}: {
  children: React.ReactNode;
  projectName?: string;
}) {
  const [state, dispatch] = useReducer(pipelineReducer, projectName, createInitialState);
  const runtimeRef = useRef<Record<string, ReturnType<typeof setInterval>>>({});
  const logIdRef = useRef(0);

  const getDefinition = useCallback((stageId: string) => {
    return PIPELINE_STAGES.find(s => s.id === stageId);
  }, []);

  const runStage = useCallback(async (
    stageId: string,
    config?: {
      model?: string;
      confidence?: number;
      summary?: string;
      findings?: string[];
      isCached?: boolean;
      isFallback?: boolean;
      simulateLog?: boolean;
    },
  ) => {
    const def = PIPELINE_STAGES.find(s => s.id === stageId);
    if (!def) return;

    dispatch({ type: "SET_ACTIVE_STAGE", stageId });
    dispatch({ type: "SET_STAGE_STATUS", stageId, status: "running" });
    dispatch({ type: "TOGGLE_EXPAND", stageId });

    // Mark cache/fallback
    if (config?.isCached) dispatch({ type: "MARK_CACHED", stageId, isCached: true });
    if (config?.isFallback) dispatch({ type: "MARK_FALLBACK", stageId, isFallback: true });

    // Set model
    if (config?.model) dispatch({ type: "SET_MODEL", stageId, model: config.model });

    // Simulate streaming log
    if (config?.simulateLog) {
      dispatch({ type: "SET_STAGE_STATUS", stageId, status: "streaming" });
      const logMessages: { text: string; type: StreamingLogEntry["type"]; delay: number }[] = [
        { text: `Starting ${def.shortName}...`, type: "info", delay: 300 },
        { text: `Loading specialist context...`, type: "info", delay: 600 },
        { text: `Running AI analysis...`, type: "ai", delay: 1200 },
        { text: `Processing results...`, type: "synthesis", delay: 1800 },
        { text: `✓ ${def.shortName} complete`, type: "complete", delay: 2400 },
      ];
      for (const msg of logMessages) {
        await new Promise(r => setTimeout(r, msg.delay));
        logIdRef.current++;
        dispatch({
          type: "ADD_LOG",
          stageId,
          entry: { id: `l-${logIdRef.current}`, text: msg.text, timestamp: Date.now(), type: msg.type },
        });
      }
    }

    // Animate progress
    dispatch({ type: "SET_PROGRESS", stageId, progress: 50 });
    await new Promise(r => setTimeout(r, 200));
    dispatch({ type: "SET_PROGRESS", stageId, progress: 80 });
    await new Promise(r => setTimeout(r, 300));
    dispatch({ type: "SET_PROGRESS", stageId, progress: 100 });

    // Set completion
    dispatch({ type: "SET_STAGE_STATUS", stageId, status: "completed" });
    if (config?.confidence) dispatch({ type: "SET_CONFIDENCE", stageId, confidence: config.confidence });
    if (config?.summary) dispatch({ type: "SET_SUMMARY", stageId, summary: config.summary });
    if (config?.findings) dispatch({ type: "SET_KEY_FINDINGS", stageId, findings: config.findings });
    dispatch({ type: "SET_RUNTIME", stageId, runtime: Math.floor(Math.random() * 4) + 2 });

    // Start next stage automatically
    const currentIdx = PIPELINE_STAGES.findIndex(s => s.id === stageId);
    const nextStage = PIPELINE_STAGES[currentIdx + 1];
    if (nextStage) {
      dispatch({ type: "SET_ACTIVE_STAGE", stageId: nextStage.id });
      dispatch({ type: "SET_STAGE_STATUS", stageId: nextStage.id, status: "waiting" });
    }
  }, [dispatch]);

  return (
    <PipelineContext.Provider value={{ state, dispatch, runStage, getDefinition }}>
      {children}
    </PipelineContext.Provider>
  );
}
