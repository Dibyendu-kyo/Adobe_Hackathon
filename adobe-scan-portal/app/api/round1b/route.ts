import { NextRequest, NextResponse } from 'next/server'
import { writeFile, unlink, mkdir } from 'fs/promises'
import { join } from 'path'
import { tmpdir } from 'os'
import { randomUUID } from 'crypto'
import { existsSync } from 'fs'

const { spawn } = require('child_process')
const path = require('path')

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    const persona = formData.get('persona') as string
    const jobToBeDone = formData.get('jobToBeDone') as string
    
    if (!files || files.length < 3) {
      return NextResponse.json({ error: 'At least 3 PDF files are required' }, { status: 400 })
    }

    if (files.length > 15) {
      return NextResponse.json({ error: 'Maximum 15 PDF files allowed' }, { status: 400 })
    }

    if (!persona || !jobToBeDone) {
      return NextResponse.json({ error: 'Persona and job description are required' }, { status: 400 })
    }

    // Check if models exist
    const modelsPath = path.join(process.cwd(), '..', 'models')
    if (!existsSync(path.join(modelsPath, 'all-MiniLM-L6-v2'))) {
      return NextResponse.json({ 
        error: 'Round 1B models not found. Please run download_models.py first.' 
      }, { status: 500 })
    }

    // Create temporary directory for this request
    const tempId = randomUUID()
    const tempDir = join(tmpdir(), `round1b_${tempId}`)
    await mkdir(tempDir, { recursive: true })

    const savedFiles: string[] = []

    try {
      // Save all uploaded files
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        if (file.type !== 'application/pdf') {
          throw new Error(`File ${file.name} is not a PDF`)
        }

        const bytes = await file.arrayBuffer()
        const buffer = Buffer.from(bytes)
        const filePath = join(tempDir, `doc_${i}_${file.name}`)
        
        await writeFile(filePath, buffer)
        savedFiles.push(filePath)
      }

      // Process with Round 1B Python script
      const startTime = Date.now()
      
      const result = await new Promise((resolve, reject) => {
        const pythonScript = path.join(process.cwd(), 'scripts', 'process_round1b_wrapper.py')
        const args = [pythonScript, modelsPath, persona, jobToBeDone, ...savedFiles]
        const python = spawn('python', args)
        
        let output = ''
        let error = ''
        
        python.stdout.on('data', (data: Buffer) => {
          output += data.toString()
        })
        
        python.stderr.on('data', (data: Buffer) => {
          error += data.toString()
        })
        
        python.on('close', (code: number) => {
          if (code === 0) {
            try {
              const jsonOutput = JSON.parse(output)
              resolve(jsonOutput)
            } catch (e) {
              reject(new Error('Failed to parse JSON output'))
            }
          } else {
            reject(new Error(`Python script failed: ${error}`))
          }
        })
      })

      const processingTime = (Date.now() - startTime) / 1000

      // Clean up temp directory
      const rimraf = require('rimraf')
      rimraf.sync(tempDir)

      return NextResponse.json({
        success: true,
        processingTime,
        documentsProcessed: files.length,
        extractedSections: (result as any).extracted_sections?.length || 0,
        result,
        constraintsMet: {
          timeLimit: processingTime <= 60,
          formatValid: typeof result === 'object' && 'metadata' in result && 'extracted_sections' in result
        }
      })

    } catch (processingError) {
      // Clean up temp directory on error
      const rimraf = require('rimraf')
      rimraf.sync(tempDir)
      
      return NextResponse.json({ 
        error: `Processing failed: ${processingError}` 
      }, { status: 500 })
    }

  } catch (error) {
    return NextResponse.json({ 
      error: `Server error: ${error}` 
    }, { status: 500 })
  }
}