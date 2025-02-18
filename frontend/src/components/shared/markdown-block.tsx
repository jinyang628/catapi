import React from "react";
import ReactMarkdown from "react-markdown";

interface StyledMessageProps {
  role: "user" | "assistant";
  content: string;
}

export default function StyledMessage({ role, content }: StyledMessageProps) {
  const baseClasses = "inline-block p-2 rounded-lg";
  const roleClasses =
    role === "user"
      ? "bg-primary text-primary-foreground"
      : "bg-secondary text-secondary-foreground";

  return (
    <div className={`${baseClasses} ${roleClasses}`}>
      <ReactMarkdown
        components={{
          a: ({ node, ...props }) => (
            <a
              className="text-blue-500 hover:text-blue-700 underline"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),
          // Style code blocks
          code: ({ node, ...props }) => (
            <code
              className="bg-gray-100 dark:bg-gray-800 px-1 rounded"
              {...props}
            />
          ),
          // Style paragraphs
          p: ({ node, ...props }) => <p className="my-1" {...props} />,
          // Style images
          img: ({ node, ...props }) => (
            <img className="max-w-full rounded-lg my-2" {...props} />
          ),
          // Style lists
          ul: ({ node, ...props }) => (
            <ul className="list-disc list-inside my-2" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal list-inside my-2" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
