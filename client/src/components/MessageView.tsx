import React, { useState } from 'react';
import { Copy, Check, Terminal, ChevronDown, ChevronRight } from 'lucide-react';
import { Message } from '../types';
import { StackedToolCalls } from './StackedToolCalls';
import { ActionApprovalCard } from './ActionApprovalCard';

interface MessageViewProps {
  message: Message;
  onDecideApproval?: (confirmationId: string, approved: boolean) => Promise<void>;
  onOpenActivity?: (messageId: string) => void;
}

export const MessageView: React.FC<MessageViewProps> = ({ message, onDecideApproval, onOpenActivity }) => {
  const isUser = message.role === 'user';
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [sleepDraftStatus, setSleepDraftStatus] = useState<string | null>(null);

  const handleCopy = (code: string, idx: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const formatContent = (content: string) => {
    if (!content) return null;

    // Split code blocks
    const parts = content.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        const lines = part.slice(3, -3).trim().split('\n');
        const lang = lines[0].match(/^[a-zA-Z0-9_-]+$/) ? lines[0] : '';
        const code = lang ? lines.slice(1).join('\n') : lines.join('\n');

        return (
          <div key={index} className="my-2.5 rounded-xl overflow-hidden border border-white/[0.08] bg-[#090b12]">
            <div className="px-3 py-1.5 bg-white/[0.03] border-b border-white/[0.06] flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span>{lang || 'code'}</span>
              <button
                onClick={() => handleCopy(code, index)}
                className="flex items-center gap-1 hover:text-white transition-colors"
              >
                {copiedIndex === index ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="p-3 text-[12px] font-mono text-slate-200 overflow-x-auto leading-relaxed">
              <code>{code}</code>
            </pre>
          </div>
        );
      }

      // Format text lines
      const lines = part.split('\n');
      return (
        <div key={index} className="space-y-1">
          {lines.map((line, lIdx) => {
            if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
              return (
                <li key={lIdx} className="ml-4 list-disc text-slate-200 my-0.5">
                  {formatInline(line.trim().substring(2))}
                </li>
              );
            }
            if (line.trim().startsWith('### ')) {
              return (
                <h4 key={lIdx} className="text-xs font-bold uppercase tracking-wider text-slate-200 mt-3 mb-1">
                  {formatInline(line.trim().substring(4))}
                </h4>
              );
            }
            if (line.trim().startsWith('## ')) {
              return (
                <h3 key={lIdx} className="text-sm font-bold text-white mt-4 mb-1">
                  {formatInline(line.trim().substring(3))}
                </h3>
              );
            }
            return (
              <p key={lIdx} className="min-h-[1.2em] leading-relaxed text-slate-200">
                {formatInline(line)}
              </p>
            );
          })}
        </div>
      );
    });
  };

  const formatInline = (text: string) => {
    const tokens = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
    return tokens.map((tok, tIdx) => {
      if (tok.startsWith('`') && tok.endsWith('`')) {
        return (
          <code key={tIdx} className="px-1.5 py-0.5 mx-0.5 rounded bg-white/[0.06] text-violet-300 font-mono text-[11px] border border-white/[0.08]">
            {tok.slice(1, -1)}
          </code>
        );
      }
      if (tok.startsWith('**') && tok.endsWith('**')) {
        return <strong key={tIdx} className="text-white font-semibold">{tok.slice(2, -2)}</strong>;
      }
      return tok;
    });
  };

  return (
    <div className={`py-2 px-1 w-full flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-2xl w-full flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-7 h-7 rounded-full bg-white/[0.08] border border-white/[0.1] flex items-center justify-center text-xs font-semibold text-slate-200">
              Y
            </div>
          ) : (
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-md shadow-violet-600/20">
              D
            </div>
          )}
        </div>

        {/* Message Content Container */}
        <div className={`flex flex-col min-w-0 ${isUser ? 'items-end' : 'items-start'} flex-1`}>
          <div
            className={`text-[13px] leading-relaxed select-text ${
              isUser
                ? 'px-4 py-2.5 rounded-2xl rounded-tr-sm bg-[#1a1c28] border border-white/[0.08] text-white shadow-sm'
                : 'w-full text-slate-200 pt-0.5'
            }`}
          >
            {message.content ? (
              <>
                {formatContent(message.content)}
                {message.isStreaming && (
                  <span className="inline-block w-1.5 h-3.5 ml-1 bg-violet-400 animate-pulse align-middle" />
                )}
              </>
            ) : (
              <span className="flex items-center gap-2 text-violet-400 text-xs font-mono py-1 animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-ping"></span>
                <span>Thinking...</span>
              </span>
            )}
          </div>

          {/* Action Approval Card (Tier 4 Privileged confirmation) */}
          {message.approvalRequest && onDecideApproval && (
            <div className="w-full">
              <ActionApprovalCard
                request={message.approvalRequest}
                onDecide={onDecideApproval}
                status={message.approvalStatus || 'pending'}
              />
            </div>
          )}

          {/* Sleep Mode In-Chat Briefing Action Bar */}
          {(message as any).sleepBriefing && (
            <div className="w-full mt-3 p-3.5 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono text-indigo-300">
                <span className="flex items-center gap-1.5 font-semibold">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  Autonomous Email Action Required
                </span>
                <span className="text-[10px] text-slate-400">
                  Status: {sleepDraftStatus || (message as any).sleepBriefing.status || 'pending'}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <button
                  disabled={!!sleepDraftStatus}
                  onClick={async () => {
                    setSleepDraftStatus('sending');
                    try {
                      await fetch(`/api/desktop/sleep/approve-draft?draft_id=${(message as any).sleepBriefing.draftId}&action=send`, { method: 'POST' });
                      setSleepDraftStatus('Sent via Gmail');
                    } catch (e) {
                      setSleepDraftStatus('Failed to send');
                    }
                  }}
                  className="px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  <span>✅ Approve & Send Reply</span>
                </button>
                <button
                  disabled={!!sleepDraftStatus}
                  onClick={async () => {
                    setSleepDraftStatus('saving');
                    try {
                      await fetch(`/api/desktop/sleep/approve-draft?draft_id=${(message as any).sleepBriefing.draftId}&action=keep`, { method: 'POST' });
                      setSleepDraftStatus('Saved in Gmail Drafts');
                    } catch (e) {
                      setSleepDraftStatus('Failed');
                    }
                  }}
                  className="px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  <span>💾 Keep in Gmail Drafts</span>
                </button>
                <button
                  disabled={!!sleepDraftStatus}
                  onClick={async () => {
                    setSleepDraftStatus('dismissed');
                    try {
                      await fetch(`/api/desktop/sleep/approve-draft?draft_id=${(message as any).sleepBriefing.draftId}&action=dismiss`, { method: 'POST' });
                    } catch (e) {}
                  }}
                  className="px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 border border-white/[0.08] text-xs font-medium transition-all disabled:opacity-50"
                >
                  <span>❌ Dismiss</span>
                </button>
              </div>
            </div>
          )}

          {/* Stacked Circular Tool Calls Badge */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className="w-full mt-1">
              <StackedToolCalls
                toolCalls={message.toolCalls}
                onOpenActivity={() => onOpenActivity?.(message.id)}
              />
            </div>
          )}

          {/* Timestamp */}
          <span className="text-[10px] text-slate-400 font-mono mt-1 px-1">
            {message.timestamp}
          </span>
        </div>
      </div>
    </div>
  );
};
