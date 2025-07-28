import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  fallback: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
  preload: true,
  adjustFontFallback: true,
})

export const metadata: Metadata = {
  title: "Adobe Pdf Extractor Project",
  description: "Secure File Scanner Powered by Adobe",
  generator: 'Adobe Pdf Extractor Project',
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: "Adobe Pdf Extractor Project",
    description: "Secure File Scanner Powered by Adobe",
    type: "website",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Preload critical resources */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
