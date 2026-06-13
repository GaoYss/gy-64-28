import { useState } from "react";

import { BarChart3, ChevronDown, ChevronRight, CircleDollarSign, Ruler, ScrollText, Users } from "lucide-react";

import { useAppData } from "../context/AppContext.jsx";

const summaryIcons = [Users, Ruler, ScrollText, CircleDollarSign];

const categoryConfig = [
  { key: "measured", label: "量房", icon: Ruler, color: "#2b6f73", customersKey: "measured_customers" },
  { key: "quoted", label: "方案", icon: ScrollText, color: "#6c5ce7", customersKey: "quoted_customers" },
  { key: "signed", label: "签约客户", icon: CircleDollarSign, color: "#166534", customersKey: "signed_customers" },
];

function CategoryCard({ category, workload }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = category.icon;
  const totalCount = workload.reduce((sum, w) => sum + w[category.key], 0);

  return (
    <article className="stat-category-card">
      <button className="stat-category-header" onClick={() => setExpanded((v) => !v)}>
        <div className="stat-category-title">
          <Icon size={20} style={{ color: category.color }} />
          <span>{category.label}</span>
        </div>
        <div className="stat-category-meta">
          <strong style={{ color: category.color }}>{totalCount}</strong>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>
      </button>
      {expanded && (
        <div className="stat-category-body">
          {workload.map((w) =>
            w[category.key] > 0 ? (
              <div className="stat-designer-group" key={w.designer}>
                <div className="stat-designer-label">
                  <div className="designer-avatar">{w.designer.charAt(0)}</div>
                  <strong>{w.designer}</strong>
                  <span className="stat-count" style={{ background: category.color }}>{w[category.key]}</span>
                </div>
                <div className="stat-customer-list">
                  {w[category.customersKey].map((c) => (
                    <div className="stat-customer-row" key={c.id}>
                      <span className="stat-customer-name">{c.name}</span>
                      <span className="stat-customer-community">{c.community}</span>
                      <span className="stat-customer-budget">¥{c.budget.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null
          )}
        </div>
      )}
    </article>
  );
}

export function DesignersPage() {
  const { designerWorkload } = useAppData();

  if (!designerWorkload) return null;

  const { summary, workload, generated_at } = designerWorkload;

  const summaryItems = [
    { label: "Designers", value: summary.total_designers, trend: "Active team" },
    { label: "Measurements", value: summary.total_measured, trend: "Site visits" },
    { label: "Quotes sent", value: summary.total_quoted, trend: "Proposals out" },
    { label: "Signed contracts", value: summary.total_signed, trend: `CNY ${summary.total_signed_budget.toLocaleString()}` },
  ];

  return (
    <div className="page-stack">
      <section className="metric-grid">
        {summaryItems.map((item, index) => {
          const Icon = summaryIcons[index] ?? BarChart3;
          return (
            <article className="metric-card" key={item.label}>
              <Icon size={20} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <small>{item.trend}</small>
            </article>
          );
        })}
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Designer Workload</h2>
          <span>{new Date(generated_at).toLocaleString()}</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Designer</th>
                <th>Measurements</th>
                <th>Quotes</th>
                <th>Signed</th>
                <th>Signed Budget</th>
                <th>Conversion</th>
              </tr>
            </thead>
            <tbody>
              {workload.map((item) => {
                const conversion = item.measured > 0
                  ? Math.round((item.signed / item.measured) * 100)
                  : 0;
                return (
                  <tr key={item.designer}>
                    <td>
                      <div className="designer-cell">
                        <div className="designer-avatar">{item.designer.charAt(0)}</div>
                        <strong>{item.designer}</strong>
                      </div>
                    </td>
                    <td>{item.measured}</td>
                    <td>{item.quoted}</td>
                    <td>
                      <span className="status-badge status-signed">{item.signed}</span>
                    </td>
                    <td>CNY {item.signed_budget.toLocaleString()}</td>
                    <td>
                      <div className="progress-cell">
                        <div className="progress-track">
                          <span style={{ width: `${Math.min(conversion, 100)}%` }} />
                        </div>
                        <strong>{conversion}%</strong>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Workload Statistics</h2>
        </div>
        <div className="stat-category-grid">
          {categoryConfig.map((cat) => (
            <CategoryCard key={cat.key} category={cat} workload={workload} />
          ))}
        </div>
      </section>
    </div>
  );
}
