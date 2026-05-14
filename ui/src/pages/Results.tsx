import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Download, FileText, Image as ImageIcon } from 'lucide-react';

const Results = () => {
  const figures = [
    { title: 'Publication Growth Timeline', desc: 'Shows CAGR post-2020 acceleration.', type: 'Figure 1' },
    { title: 'Keyword Co-occurrence Network', desc: 'Thematic clusters and interconnections.', type: 'Figure 2' },
    { title: 'Geopolitical Collaboration Map', desc: 'Top countries and their research links.', type: 'Figure 3' },
    { title: 'Thematic Evolution', desc: 'How topics changed from 2010 to 2024.', type: 'Figure 4' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>Final Results</h1>
          <p>The final research report and manuscript-ready visualizations.</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-outline">
            <Download size={18} />
            Export All
          </button>
          <button className="btn btn-primary">
            <FileText size={18} />
            View Full Report
          </button>
        </div>
      </header>

      <div className="grid-2">
        {figures.map((fig, i) => (
          <div key={i} className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ 
              height: '240px', 
              background: 'var(--bg-tertiary)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              borderBottom: '1px solid var(--border-color)'
            }}>
              <ImageIcon size={48} color="var(--text-muted)" />
            </div>
            <div style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-primary)', textTransform: 'uppercase' }}>{fig.type}</span>
                  <h3 style={{ marginTop: '0.25rem' }}>{fig.title}</h3>
                </div>
                <button className="btn btn-outline" style={{ padding: '0.5rem' }}>
                  <ExternalLink size={16} />
                </button>
              </div>
              <p style={{ fontSize: '0.85rem', margin: 0 }}>{fig.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <div style={{ display: 'flex', gap: '2rem' }}>
          <div style={{ flex: 1 }}>
            <h3>Executive Discussion Draft</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.8 }}>
              The findings indicate a significant shift in scholarly communication towards integrated research security frameworks. 
              The post-2020 period saw a 34% increase in publications addressing the intersection of open data and institutional 
              vulnerability. Key emerging clusters include "AI-Aware Governance" and "Distributed Repository Security"...
            </p>
            <button className="btn btn-outline" style={{ marginTop: '1rem' }}>Edit with AI Assistant</button>
          </div>
          <div style={{ width: '300px', paddingLeft: '2rem', borderLeft: '1px solid var(--border-color)' }}>
            <h3>Report Details</h3>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Generated:</span>
                <span>May 14, 2026</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Papers Analyzed:</span>
                <span>4,786</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Core Themes:</span>
                <span>12</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Format:</span>
                <span>Markdown, PDF</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Results;
