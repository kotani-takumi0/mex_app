/**
 * カテゴリ分布バー
 * ドキュメントのカテゴリ構成を水平バーで可視化。
 * ドキュメント5件未満では非表示（少数時は逆効果のため）。
 */
import React, { useMemo } from 'react';
import { TechDocument } from '../../types';
import { getCategoryLabel } from '../../utils/category';
import './CategoryDistribution.css';

interface CategoryDistributionProps {
  readonly documents: TechDocument[];
}

const categoryColors: Record<string, string> = {
  tutorial: '#ffab2e',
  design: '#2cbb5d',
  debug_guide: '#ffc01e',
  learning: '#a855f7',
  reference: 'rgba(239, 241, 246, 0.4)',
};

export const CategoryDistribution: React.FC<CategoryDistributionProps> = ({ documents }) => {
  const distribution = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const doc of documents) {
      counts[doc.category] = (counts[doc.category] || 0) + 1;
    }
    return Object.entries(counts)
      .map(([category, count]) => ({
        category: category as TechDocument['category'],
        count,
        ratio: count / documents.length,
      }))
      .sort((a, b) => b.count - a.count);
  }, [documents]);

  if (documents.length < 5) return null;

  return (
    <div className="category-distribution">
      <div className="distribution-bar">
        {distribution.map(({ category, ratio }) => (
          <div
            key={category}
            className="distribution-segment"
            style={{
              width: `${ratio * 100}%`,
              backgroundColor: categoryColors[category] || categoryColors.reference,
            }}
            title={getCategoryLabel(category)}
          />
        ))}
      </div>
      <div className="distribution-legend">
        {distribution.map(({ category, count }) => (
          <span key={category} className="distribution-legend-item">
            <span
              className="distribution-dot"
              style={{ backgroundColor: categoryColors[category] || categoryColors.reference }}
            />
            {getCategoryLabel(category)} {count}
          </span>
        ))}
      </div>
    </div>
  );
};
