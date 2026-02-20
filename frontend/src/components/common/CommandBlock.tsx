/**
 * コマンドコピーUIコンポーネント
 *
 * 変更理由: SettingsPageにローカル定義されていたCommandBlockを
 * SetupWizardPageでも再利用するため共通コンポーネントに抽出。
 */
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { LuCopy, LuCheck } from 'react-icons/lu';
import './CommandBlock.css';

export const copyToClipboard = async (text: string) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  const success = document.execCommand('copy');
  document.body.removeChild(textarea);
  if (!success) {
    throw new Error('copy failed');
  }
};

export const CommandBlock: React.FC<{ command: string }> = ({ command }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await copyToClipboard(command);
      setCopied(true);
      toast.success('コマンドをコピーしました');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('コピーに失敗しました');
    }
  };

  return (
    <div className="command-block">
      <code className="command-block-text">{command}</code>
      <button type="button" className="command-block-copy" onClick={handleCopy}>
        {copied ? <LuCheck size={14} /> : <LuCopy size={14} />}
      </button>
    </div>
  );
};
