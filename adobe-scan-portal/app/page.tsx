"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, FileText, Shield, CheckCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function AdobeScanPortal() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [scanResults, setScanResults] = useState<any>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file)
    setScanResults(null)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        handleFileSelect(files[0])
      }
    },
    [handleFileSelect],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        handleFileSelect(files[0])
      }
    },
    [handleFileSelect],
  )

  const handleScan = async () => {
    if (!selectedFile) return

    setIsScanning(true)

    // Simulate scanning process
    await new Promise((resolve) => setTimeout(resolve, 3000))

    // Mock scan results
    setScanResults({
      status: "clean",
      threats: 0,
      fileType: selectedFile.type || "unknown",
      size: selectedFile.size,
      scanTime: "2.3s",
      details: [
        { category: "Malware", status: "clean", icon: CheckCircle },
        { category: "Suspicious Content", status: "clean", icon: CheckCircle },
        { category: "Data Extraction", status: "complete", icon: CheckCircle },
      ],
    })

    setIsScanning(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Navbar */}
      <motion.nav initial={{ y: -100 }} animate={{ y: 0 }} className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="bg-red-600 text-white px-3 py-1 rounded font-bold text-lg">Adobe</div>
              </div>
            </div>
            <Button
              variant="outline"
              className="border-red-600 text-red-600 hover:bg-red-600 hover:text-white bg-transparent"
            >
              Login
            </Button>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-red-600 to-red-700 text-white py-20"
      >
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">Secure File Scanner Powered by Adobe</h1>
          <p className="text-xl md:text-2xl text-red-100 max-w-3xl mx-auto">
            Upload any file to scan for threats, content, or extract intelligence.
          </p>
        </div>
      </motion.section>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Upload Card */}
        <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="bg-gradient-to-br from-white to-gray-50 shadow-xl border-0 rounded-2xl overflow-hidden">
            <CardContent className="p-8">
              <div
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                  isDragOver
                    ? "border-red-500 bg-red-50"
                    : selectedFile
                      ? "border-green-500 bg-green-50"
                      : "border-gray-300 hover:border-red-400 hover:bg-red-50"
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
              >
                <input type="file" id="file-upload" className="hidden" onChange={handleFileInput} accept="*/*" />

                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center space-y-4">
                      {selectedFile ? (
                        <FileText className="w-16 h-16 text-green-600" />
                      ) : (
                        <Upload className="w-16 h-16 text-gray-400" />
                      )}

                      {selectedFile ? (
                        <div className="text-center">
                          <p className="text-lg font-semibold text-green-700">{selectedFile.name}</p>
                          <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <p className="text-lg font-semibold text-gray-700">Drop your file here or click to browse</p>
                          <p className="text-sm text-gray-500">Supports all file types</p>
                        </div>
                      )}
                    </div>
                  </label>
                </motion.div>
              </div>

              <div className="mt-8 text-center">
                <Button
                  onClick={handleScan}
                  disabled={!selectedFile || isScanning}
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-lg font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isScanning ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <Shield className="w-5 h-5 mr-2" />
                      Scan File
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Loading Animation */}
        <AnimatePresence>
          {isScanning && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8"
            >
              <Card className="bg-white shadow-lg rounded-xl">
                <CardContent className="p-8 text-center">
                  <div className="flex flex-col items-center space-y-4">
                    <div className="relative">
                      <div className="w-16 h-16 border-4 border-red-200 rounded-full"></div>
                      <div className="absolute top-0 left-0 w-16 h-16 border-4 border-red-600 rounded-full border-t-transparent animate-spin"></div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">Analyzing File</h3>
                      <p className="text-gray-600">Please wait while we scan your file...</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Card */}
        <AnimatePresence>
          {scanResults && !isScanning && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8"
            >
              <Card className="bg-white shadow-lg rounded-xl border-l-4 border-l-green-500">
                <CardContent className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-gray-800">Scan Results</h3>
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-6 h-6 text-green-600" />
                      <span className="text-green-600 font-semibold">Clean</span>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">File Type</p>
                      <p className="font-semibold text-gray-800">{scanResults.fileType}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">File Size</p>
                      <p className="font-semibold text-gray-800">{(scanResults.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">Scan Time</p>
                      <p className="font-semibold text-gray-800">{scanResults.scanTime}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">Threats Found</p>
                      <p className="font-semibold text-green-600">{scanResults.threats}</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-800">Detailed Analysis</h4>
                    {scanResults.details.map((detail: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <detail.icon className="w-5 h-5 text-green-600" />
                          <span className="font-medium text-gray-800">{detail.category}</span>
                        </div>
                        <span className="text-green-600 font-semibold capitalize">{detail.status}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-300">
              © 2025 Adobe Secure Services |
              <a href="#" className="text-red-400 hover:text-red-300 mx-2">
                Privacy
              </a>{" "}
              |
              <a href="#" className="text-red-400 hover:text-red-300 mx-2">
                Terms
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
