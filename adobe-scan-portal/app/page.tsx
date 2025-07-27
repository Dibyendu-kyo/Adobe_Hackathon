"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, FileText, Shield, CheckCircle, Loader2, Brain, FileSearch, Users, Target } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

type ProcessingMode = 'round1a' | 'round1b'

export default function AdobeScanPortal() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [activeTab, setActiveTab] = useState<ProcessingMode>('round1a')
  const [persona, setPersona] = useState('Travel Planner')
  const [jobToBeDone, setJobToBeDone] = useState('Plan a 4-day trip for a group of 10 college friends')
  const [showAllHeadings, setShowAllHeadings] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set())

  const toggleSectionExpansion = (index: number) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSections(newExpanded)
  }

  const handleFileSelect = useCallback((files: File[]) => {
    setSelectedFiles(files)
    setResults(null)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf')
      if (files.length > 0) {
        if (activeTab === 'round1a') {
          handleFileSelect([files[0]])
        } else {
          // For Round 1B, add new files to existing ones (up to 15 total)
          if (selectedFiles.length < 15) {
            const availableSlots = 15 - selectedFiles.length
            const filesToAdd = files.slice(0, availableSlots)
            const newFiles = [...selectedFiles, ...filesToAdd]
            handleFileSelect(newFiles)
          }
        }
      }
    },
    [handleFileSelect, activeTab, selectedFiles],
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
        const pdfFiles = Array.from(files).filter(f => f.type === 'application/pdf')
        if (activeTab === 'round1a') {
          handleFileSelect([pdfFiles[0]])
        } else {
          // For Round 1B, add new files to existing ones (up to 15 total)
          if (selectedFiles.length < 15) {
            const availableSlots = 15 - selectedFiles.length
            const filesToAdd = pdfFiles.slice(0, availableSlots)
            const newFiles = [...selectedFiles, ...filesToAdd]
            handleFileSelect(newFiles)
          }
        }
      }
      // Reset the input so the same file can be selected again if needed
      e.target.value = ''
    },
    [handleFileSelect, activeTab, selectedFiles],
  )

  const handleProcess = async () => {
    if (selectedFiles.length === 0) return

    setIsProcessing(true)
    setResults(null)

    try {
      if (activeTab === 'round1a') {
        // Process Round 1A
        const formData = new FormData()
        formData.append('file', selectedFiles[0])

        const response = await fetch('/api/round1a', {
          method: 'POST',
          body: formData,
        })

        const result = await response.json()
        setResults(result)
      } else {
        // Process Round 1B
        const formData = new FormData()
        selectedFiles.forEach(file => {
          formData.append('files', file)
        })
        formData.append('persona', persona)
        formData.append('jobToBeDone', jobToBeDone)

        const response = await fetch('/api/round1b', {
          method: 'POST',
          body: formData,
        })

        const result = await response.json()
        setResults(result)
      }
    } catch (error) {
      setResults({
        success: false,
        error: `Processing failed: ${error}`
      })
    }

    setIsProcessing(false)
  }

  return (
    <div className="min-h-screen bg-white font-sans">
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
          <h1 className="text-4xl md:text-6xl font-bold mb-6">Adobe Hackathon PDF Processing</h1>
          <p className="text-xl md:text-2xl text-red-100 max-w-3xl mx-auto">
            Round 1A: Document Structure Extraction | Round 1B: Persona-Driven Intelligence
          </p>
        </div>
      </motion.section>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Challenge Selection Tabs */}
        <motion.div initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Tabs value={activeTab} onValueChange={(value) => {
            setActiveTab(value as ProcessingMode)
            setSelectedFiles([])
            setResults(null)
          }} className="w-full">
            <div className="flex justify-center mb-8">
              <div className="bg-gray-100 p-1 rounded-lg border-2 border-gray-300">
                <div className="flex">
                  <button
                    onClick={() => {
                      setActiveTab('round1a')
                      setSelectedFiles([])
                      setResults(null)
                    }}
                    className={`px-6 py-3 rounded-md font-bold text-base transition-all ${
                      activeTab === 'round1a'
                        ? 'bg-white text-black shadow-md border border-gray-300'
                        : 'text-gray-700 hover:text-black'
                    }`}
                  >
                    Round 1A: Document Structure
                  </button>
                  <button
                    onClick={() => {
                      setActiveTab('round1b')
                      setSelectedFiles([])
                      setResults(null)
                    }}
                    className={`px-6 py-3 rounded-md font-bold text-base transition-all ${
                      activeTab === 'round1b'
                        ? 'bg-white text-black shadow-md border border-gray-300'
                        : 'text-gray-700 hover:text-black'
                    }`}
                  >
                    Round 1B: Persona Intelligence
                  </button>
                </div>
              </div>
            </div>

            <TabsContent value="round1a">
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Round 1A Upload */}
                <Card className="bg-white shadow-lg border-2 border-gray-300 rounded-xl">
                  <CardContent className="p-8">
                    <div className="mb-6">
                      <h3 className="text-2xl font-bold text-black mb-2">Document Structure Extraction</h3>
                      <p className="text-gray-800 font-medium">Upload a single PDF to extract title and headings (H1, H2, H3)</p>
                      <div className="flex space-x-2 mt-3">
                        <span className="px-3 py-1 bg-blue-600 text-white text-sm font-bold rounded">≤10s processing</span>
                        <span className="px-3 py-1 bg-green-600 text-white text-sm font-bold rounded">Single PDF</span>
                      </div>
                    </div>

                    <div
                      className={`border-3 border-dashed rounded-2xl p-10 text-center transition-all duration-300 ${
                        isDragOver
                          ? "border-blue-500 bg-blue-50 shadow-lg transform scale-105"
                          : selectedFiles.length > 0
                            ? "border-green-500 bg-gradient-to-br from-green-50 to-emerald-50 shadow-md"
                            : "border-gray-300 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50 hover:shadow-md"
                      }`}
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                    >
                      <input 
                        type="file" 
                        id="file-upload-1a" 
                        className="hidden" 
                        onChange={handleFileInput} 
                        accept=".pdf"
                        multiple={false}
                      />

                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <label htmlFor="file-upload-1a" className="cursor-pointer">
                          <div className="flex flex-col items-center space-y-4">
                            {selectedFiles.length > 0 ? (
                              <FileText className="w-12 h-12 text-green-600" />
                            ) : (
                              <Upload className="w-12 h-12 text-gray-400" />
                            )}

                            {selectedFiles.length > 0 ? (
                              <div className="text-center">
                                <p className="text-lg font-bold text-green-800">{selectedFiles[0].name}</p>
                                <p className="text-sm font-medium text-gray-700">{(selectedFiles[0].size / 1024 / 1024).toFixed(2)} MB</p>
                              </div>
                            ) : (
                              <div className="text-center">
                                <p className="text-lg font-bold text-gray-900">Drop PDF here or click to browse</p>
                                <p className="text-sm font-medium text-gray-700">Single PDF file only</p>
                              </div>
                            )}
                          </div>
                        </label>
                      </motion.div>
                    </div>

                    <div className="mt-6 text-center">
                      <Button
                        onClick={handleProcess}
                        disabled={selectedFiles.length === 0 || isProcessing}
                        className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 text-lg font-semibold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isProcessing ? (
                          <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          <>
                            <FileSearch className="w-5 h-5 mr-2" />
                            Extract Structure
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Round 1A Results */}
                <Card className="bg-white shadow-lg rounded-xl border-2 border-gray-200">
                  <CardContent className="p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-gray-200 pb-3">Results</h3>
                    
                    {isProcessing && activeTab === 'round1a' && (
                      <div className="text-center py-8">
                        <div className="relative mx-auto w-16 h-16 mb-4">
                          <div className="w-16 h-16 border-4 border-red-200 rounded-full"></div>
                          <div className="absolute top-0 left-0 w-16 h-16 border-4 border-red-600 rounded-full border-t-transparent animate-spin"></div>
                        </div>
                        <p className="text-gray-600">Extracting document structure...</p>
                      </div>
                    )}

                    {results && activeTab === 'round1a' && !isProcessing && (
                      <div className="space-y-4">
                        {results.success ? (
                          <>
                            <div className="grid grid-cols-2 gap-4 mb-4">
                              <div className="bg-gray-100 p-3 rounded border">
                                <p className="text-sm text-gray-700 font-medium">Processing Time</p>
                                <p className="font-bold text-gray-900 text-lg">{results.processingTime?.toFixed(3)}s</p>
                              </div>
                              <div className="bg-gray-100 p-3 rounded border">
                                <p className="text-sm text-gray-700 font-medium">Headings Found</p>
                                <p className="font-bold text-gray-900 text-lg">{results.result?.outline?.length || 0}</p>
                              </div>
                            </div>
                            
                            <div className="mb-4">
                              <p className="text-sm text-gray-700 font-medium mb-2">Document Title:</p>
                              <p className="font-semibold text-gray-900 bg-gray-100 p-3 rounded border">{results.result?.title || 'N/A'}</p>
                            </div>

                            <div className="flex space-x-2 mb-4">
                              <span className={`px-2 py-1 text-xs rounded ${results.constraintsMet?.timeLimit ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                Time: {results.constraintsMet?.timeLimit ? '✓' : '✗'}
                              </span>
                              <span className={`px-2 py-1 text-xs rounded ${results.constraintsMet?.formatValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                Format: {results.constraintsMet?.formatValid ? '✓' : '✗'}
                              </span>
                            </div>

                            {results.result?.outline && results.result.outline.length > 0 && (
                              <div>
                                <p className="text-base font-bold text-gray-900 mb-3">Document Outline:</p>
                                <div className="max-h-64 overflow-y-auto bg-white border-2 border-gray-300 rounded-lg shadow-sm">
                                  {(showAllHeadings ? results.result.outline : results.result.outline.slice(0, 10)).map((heading: any, index: number) => (
                                    <div key={index} className="flex justify-between items-center py-3 px-4 border-b border-gray-200 last:border-b-0 hover:bg-gray-50">
                                      <span className={`text-gray-900 ${heading.level === 'H1' ? 'font-bold text-lg text-blue-900' : heading.level === 'H2' ? 'font-semibold text-base ml-4 text-green-800' : 'font-medium text-sm ml-8 text-purple-800'}`}>
                                        <span className="inline-block w-8 text-xs font-bold text-gray-600">{heading.level}:</span>
                                        {heading.text}
                                      </span>
                                      <span className="text-gray-800 font-bold text-sm bg-gray-100 px-2 py-1 rounded">p{heading.page}</span>
                                    </div>
                                  ))}
                                  {results.result.outline.length > 10 && (
                                    <div className="text-center py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-t-2 border-blue-200">
                                      <p className="text-blue-900 font-bold text-sm mb-2">
                                        📋 {showAllHeadings ? 'All headings shown' : `${results.result.outline.length - 10} more headings available`}
                                      </p>
                                      <button 
                                        onClick={() => setShowAllHeadings(!showAllHeadings)}
                                        className="text-blue-700 hover:text-blue-900 font-bold text-xs underline hover:no-underline transition-all"
                                      >
                                        {showAllHeadings ? '📤 Show Less' : '📋 Show All Headings'}
                                      </button>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-center py-8">
                            <div className="text-red-600 mb-2">
                              <Shield className="w-12 h-12 mx-auto" />
                            </div>
                            <p className="text-red-600 font-semibold">Processing Failed</p>
                            <p className="text-gray-600 text-sm mt-2">{results.error}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {!results && !isProcessing && (
                      <div className="text-center py-8">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p className="text-gray-700 font-medium text-lg">Upload a PDF to see results here</p>
                        <p className="text-gray-600 text-sm mt-2">Results will appear with document structure and headings</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="round1b">
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Round 1B Upload */}
                <Card className="bg-white shadow-lg border-2 border-gray-300 rounded-xl">
                  <CardContent className="p-8">
                    <div className="mb-6">
                      <h3 className="text-2xl font-bold text-black mb-2">Persona-Driven Intelligence</h3>
                      <p className="text-gray-800 font-medium">Upload 3-15 related PDFs and define your persona and task</p>
                      <div className="flex space-x-2 mt-3">
                        <span className="px-3 py-1 bg-purple-600 text-white text-sm font-bold rounded">≤60s processing</span>
                        <span className="px-3 py-1 bg-orange-600 text-white text-sm font-bold rounded">3-15 PDFs</span>
                      </div>
                    </div>

                    <div
                      className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 mb-4 ${
                        isDragOver
                          ? "border-purple-500 bg-purple-50"
                          : selectedFiles.length > 0
                            ? "border-green-500 bg-green-50"
                            : "border-gray-400 hover:border-purple-400 hover:bg-purple-50"
                      }`}
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                    >
                      <input 
                        type="file" 
                        id="file-upload-1b" 
                        className="hidden" 
                        onChange={handleFileInput} 
                        accept=".pdf"
                        multiple={true}
                      />

                      <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                        <label htmlFor="file-upload-1b" className="cursor-pointer">
                          <div className="flex flex-col items-center space-y-4">
                            {selectedFiles.length > 0 ? (
                              <FileText className="w-12 h-12 text-green-600" />
                            ) : (
                              <Upload className="w-12 h-12 text-gray-500" />
                            )}

                            {selectedFiles.length > 0 ? (
                              <div className="text-center">
                                <p className="text-xl font-bold text-green-800 mb-2">{selectedFiles.length} PDFs Selected</p>
                                <div className="bg-white border border-gray-300 rounded-lg p-3 max-h-24 overflow-y-auto">
                                  {selectedFiles.map((file, index) => (
                                    <div key={index} className="flex justify-between items-center text-sm font-medium text-gray-800 py-1">
                                      <span>📄 {file.name}</span>
                                      <button
                                        onClick={(e) => {
                                          e.preventDefault()
                                          e.stopPropagation()
                                          const newFiles = selectedFiles.filter((_, i) => i !== index)
                                          handleFileSelect(newFiles)
                                        }}
                                        className="text-red-600 hover:text-red-800 font-bold text-xs ml-2"
                                      >
                                        ✕
                                      </button>
                                    </div>
                                  ))}
                                </div>
                                <div className="flex justify-between items-center mt-2">
                                  <p className="text-sm text-gray-600">
                                    {selectedFiles.length >= 3 && selectedFiles.length <= 15 
                                      ? "✅ Ready to analyze" 
                                      : selectedFiles.length < 3 
                                        ? `Need ${3 - selectedFiles.length} more files` 
                                        : "Too many files (max 15)"}
                                  </p>
                                  <button
                                    onClick={(e) => {
                                      e.preventDefault()
                                      e.stopPropagation()
                                      handleFileSelect([])
                                    }}
                                    className="text-red-600 hover:text-red-800 font-bold text-xs underline"
                                  >
                                    Clear All
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <div className="text-center">
                                <p className="text-xl font-bold text-gray-900 mb-2">Upload Multiple PDFs</p>
                                <p className="text-base font-medium text-gray-700">Drop 3-15 related PDF files here or click to browse</p>
                                <p className="text-sm text-gray-600 mt-2">Multiple file selection supported</p>
                              </div>
                            )}
                          </div>
                        </label>
                      </motion.div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label htmlFor="persona" className="block text-sm font-bold text-black mb-2">Persona</label>
                        <Input
                          id="persona"
                          value={persona}
                          onChange={(e) => setPersona(e.target.value)}
                          placeholder="e.g., Travel Planner, Food Critic, Investment Analyst"
                          className="w-full p-3 border-2 border-gray-300 rounded-lg text-black font-medium bg-white"
                        />
                      </div>

                      <div>
                        <label htmlFor="job" className="block text-sm font-bold text-black mb-2">Job to be Done</label>
                        <Textarea
                          id="job"
                          value={jobToBeDone}
                          onChange={(e) => setJobToBeDone(e.target.value)}
                          placeholder="Describe the specific task or goal..."
                          className="w-full p-3 border-2 border-gray-300 rounded-lg text-black font-medium bg-white"
                          rows={3}
                        />
                      </div>
                    </div>

                    <div className="mt-6 text-center">
                      <Button
                        onClick={handleProcess}
                        disabled={selectedFiles.length < 3 || selectedFiles.length > 15 || isProcessing || !persona.trim() || !jobToBeDone.trim()}
                        className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-xl font-bold rounded-lg disabled:opacity-50 disabled:cursor-not-allowed shadow-lg border-2 border-red-700"
                      >
                        {isProcessing ? (
                          <>
                            <Loader2 className="w-6 h-6 mr-3 animate-spin" />
                            <span className="font-bold">Analyzing...</span>
                          </>
                        ) : (
                          <>
                            <Brain className="w-6 h-6 mr-3" />
                            <span className="font-bold">Analyze Documents</span>
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Round 1B Results */}
                <Card className="bg-white shadow-lg rounded-xl border-2 border-gray-200">
                  <CardContent className="p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-gray-200 pb-3">Analysis Results</h3>
                    
                    {isProcessing && activeTab === 'round1b' && (
                      <div className="text-center py-8">
                        <div className="relative mx-auto w-16 h-16 mb-4">
                          <div className="w-16 h-16 border-4 border-red-200 rounded-full"></div>
                          <div className="absolute top-0 left-0 w-16 h-16 border-4 border-red-600 rounded-full border-t-transparent animate-spin"></div>
                        </div>
                        <p className="text-gray-600">Analyzing documents with AI...</p>
                        <p className="text-gray-500 text-sm mt-1">This may take up to 60 seconds</p>
                      </div>
                    )}

                    {results && activeTab === 'round1b' && !isProcessing && (
                      <div className="space-y-4">
                        {results.success ? (
                          <>
                            <div className="grid grid-cols-3 gap-4 mb-4">
                              <div className="bg-gray-100 p-3 rounded border text-center">
                                <p className="text-sm text-gray-700 font-medium">Time</p>
                                <p className="font-bold text-gray-900 text-lg">{results.processingTime?.toFixed(1)}s</p>
                              </div>
                              <div className="bg-gray-100 p-3 rounded border text-center">
                                <p className="text-sm text-gray-700 font-medium">Documents</p>
                                <p className="font-bold text-gray-900 text-lg">{results.documentsProcessed}</p>
                              </div>
                              <div className="bg-gray-100 p-3 rounded border text-center">
                                <p className="text-sm text-gray-700 font-medium">Sections</p>
                                <p className="font-bold text-gray-900 text-lg">{results.extractedSections}</p>
                              </div>
                            </div>

                            <div className="flex space-x-2 mb-4">
                              <span className={`px-2 py-1 text-xs rounded ${results.constraintsMet?.timeLimit ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                Time: {results.constraintsMet?.timeLimit ? '✓' : '✗'}
                              </span>
                              <span className={`px-2 py-1 text-xs rounded ${results.constraintsMet?.formatValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                Format: {results.constraintsMet?.formatValid ? '✓' : '✗'}
                              </span>
                            </div>

                            {results.result?.extracted_sections && results.result.extracted_sections.length > 0 && (
                              <div>
                                <p className="text-base font-bold text-gray-900 mb-3">Top Relevant Sections:</p>
                                <div className="space-y-3">
                                  {results.result.extracted_sections.slice(0, 5).map((section: any, index: number) => (
                                    <div key={index} className="bg-white border-2 border-gray-300 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                                      <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                          <div className="flex items-center mb-2">
                                            <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full mr-2">
                                              #{section.importance_rank}
                                            </span>
                                            <h4 className="font-bold text-gray-900 text-base">
                                              {section.section_title}
                                            </h4>
                                          </div>
                                          <div className="flex items-center text-sm text-gray-700 mb-2">
                                            <span className="bg-gray-100 px-2 py-1 rounded text-xs font-medium mr-2">
                                              📄 {section.document}
                                            </span>
                                            <span className="bg-gray-100 px-2 py-1 rounded text-xs font-medium">
                                              📍 Page {section.page_number}
                                            </span>
                                          </div>
                                          {/* Show detailed content if available */}
                                          {results.result?.subsection_analysis && results.result.subsection_analysis[index] && (
                                            <div className="mt-3 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                                              <p className="text-sm text-gray-800 leading-relaxed">
                                                {expandedSections.has(index) 
                                                  ? results.result.subsection_analysis[index].refined_text
                                                  : `${results.result.subsection_analysis[index].refined_text.substring(0, 200)}${results.result.subsection_analysis[index].refined_text.length > 200 ? '...' : ''}`
                                                }
                                              </p>
                                              {results.result.subsection_analysis[index].refined_text.length > 200 && (
                                                <button
                                                  onClick={() => toggleSectionExpansion(index)}
                                                  className="mt-2 text-blue-600 hover:text-blue-800 font-bold text-xs underline hover:no-underline transition-all"
                                                >
                                                  {expandedSections.has(index) ? '📤 Show Less' : '📋 Show More'}
                                                </button>
                                              )}
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                                
                                {/* Show metadata if available */}
                                {results.result?.metadata && (
                                  <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
                                    <h4 className="font-bold text-gray-900 mb-2">Analysis Summary</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                                      <div>
                                        <span className="font-medium text-gray-700">Persona:</span>
                                        <span className="ml-2 text-gray-900 font-semibold">{results.result.metadata.persona}</span>
                                      </div>
                                      <div>
                                        <span className="font-medium text-gray-700">Documents:</span>
                                        <span className="ml-2 text-gray-900 font-semibold">{results.result.metadata.input_documents?.length || 0}</span>
                                      </div>
                                      <div className="md:col-span-2">
                                        <span className="font-medium text-gray-700">Task:</span>
                                        <p className="mt-1 text-gray-900 font-medium">{results.result.metadata.job_to_be_done}</p>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-center py-8">
                            <div className="text-red-600 mb-2">
                              <Brain className="w-12 h-12 mx-auto" />
                            </div>
                            <p className="text-red-600 font-semibold">Analysis Failed</p>
                            <p className="text-gray-600 text-sm mt-2">{results.error}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {!results && !isProcessing && (
                      <div className="text-center py-8">
                        <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p className="text-gray-700 font-medium text-lg">Upload documents and configure persona to see results</p>
                        <p className="text-gray-600 text-sm mt-2">AI analysis will show the most relevant sections for your task</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
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
