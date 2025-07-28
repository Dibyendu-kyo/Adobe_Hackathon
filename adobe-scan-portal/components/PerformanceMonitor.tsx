"use client"

import { useEffect, useState } from 'react'
import { Clock, Zap, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface PerformanceMetrics {
  processingTime: number
  fileSize: number
  memoryUsage?: number
  isOptimized: boolean
}

interface PerformanceMonitorProps {
  metrics: PerformanceMetrics | null
  isProcessing: boolean
}

export function PerformanceMonitor({ metrics, isProcessing }: PerformanceMonitorProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    if (metrics || isProcessing) {
      setIsVisible(true)
    } else {
      const timer = setTimeout(() => setIsVisible(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [metrics, isProcessing])

  if (!isVisible) return null

  const getPerformanceStatus = (time: number) => {
    if (time <= 5) return { color: 'text-green-600', icon: Zap, label: 'Excellent' }
    if (time <= 10) return { color: 'text-yellow-600', icon: Clock, label: 'Good' }
    return { color: 'text-red-600', icon: AlertCircle, label: 'Slow' }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed bottom-4 right-4 z-50"
    >
      <Card className="w-80 shadow-lg border-l-4 border-blue-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Performance Monitor
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {isProcessing ? (
            <div className="flex items-center gap-2 text-sm">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span>Processing...</span>
            </div>
          ) : metrics ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span>Processing Time:</span>
                <div className="flex items-center gap-1">
                  {(() => {
                    const status = getPerformanceStatus(metrics.processingTime)
                    const Icon = status.icon
                    return (
                      <>
                        <Icon className={`h-4 w-4 ${status.color}`} />
                        <span className={status.color}>
                          {metrics.processingTime.toFixed(2)}s ({status.label})
                        </span>
                      </>
                    )
                  })()}
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span>File Size:</span>
                <span className="text-gray-600">{formatFileSize(metrics.fileSize)}</span>
              </div>
              
              {metrics.memoryUsage && (
                <div className="flex justify-between items-center">
                  <span>Memory Usage:</span>
                  <span className="text-gray-600">{formatFileSize(metrics.memoryUsage)}</span>
                </div>
              )}
              
              <div className="flex justify-between items-center">
                <span>Optimized:</span>
                <span className={metrics.isOptimized ? 'text-green-600' : 'text-red-600'}>
                  {metrics.isOptimized ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </motion.div>
  )
}

import { motion } from 'framer-motion' 