import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import './MarkdownRenderer.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Style blockquotes as hooks (intro text)
          blockquote: ({ children }) => (
            <blockquote className="hook">{children}</blockquote>
          ),
          // Add section-divider class to hr
          hr: () => <hr className="section-divider" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
