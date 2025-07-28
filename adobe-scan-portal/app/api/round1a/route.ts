import { NextRequest, NextResponse } from 'next/server'
import { writeFile, unlink } from 'fs/promises'
import { join } from 'path'
import { tmpdir } from 'os'
import { randomUUID } from 'crypto'

// Import the Round 1A extractor
const { spawn } = require('child_process')
const path = require('path')

// Constants for optimization
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB limit
const PROCESS_TIMEOUT = 30000 // 30 seconds timeout
const CLEANUP_TIMEOUT = 5000 // 5 seconds for cleanup

export async function POST(request: NextRequest) {
  const startTime = Date.now()
  let tempFilePath: string | null = null
  
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'Only PDF files are supported' }, { status: 400 })
    }

    // File size validation
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json({ 
        error: `File too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB` 
      }, { status: 400 })
    }

    // Save the uploaded file temporarily with optimized buffer handling
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    
    const tempId = randomUUID()
    tempFilePath = join(tmpdir(), `upload_${tempId}.pdf`)
    
    await writeFile(tempFilePath, buffer)

    // Process with Round 1A Python script with timeout
    const result = await new Promise((resolve, reject) => {
      const pythonScript = path.join(process.cwd(), 'scripts', 'process_round1a_wrapper.py')
      const python = spawn('python', [pythonScript, tempFilePath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: PROCESS_TIMEOUT
      })
      
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
            reject(new Error(`Failed to parse JSON output: ${e}`))
          }
        } else {
          reject(new Error(`Python script failed with code ${code}: ${error}`))
        }
      })
      
      python.on('error', (err: Error) => {
        reject(new Error(`Failed to start Python process: ${err.message}`))
      })

      python.on('timeout', () => {
        python.kill('SIGKILL')
        reject(new Error('Processing timeout exceeded'))
      })
    })

    const processingTime = (Date.now() - startTime) / 1000

    // Clean up temp file with timeout
    if (tempFilePath) {
      try {
        await Promise.race([
          unlink(tempFilePath),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Cleanup timeout')), CLEANUP_TIMEOUT)
          )
        ])
      } catch (cleanupError) {
        console.warn('Failed to cleanup temp file:', cleanupError)
      }
    }

    return NextResponse.json({
      success: true,
      processingTime,
      result,
      constraintsMet: {
        timeLimit: processingTime <= 10,
        formatValid: typeof result === 'object' && 'title' in result && 'outline' in result
      }
    })

  } catch (error) {
    // Clean up temp file on error
    if (tempFilePath) {
      try {
        await Promise.race([
          unlink(tempFilePath),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Cleanup timeout')), CLEANUP_TIMEOUT)
          )
        ])
      } catch (cleanupError) {
        console.warn('Failed to cleanup temp file on error:', cleanupError)
      }
    }
    
    const errorMessage = error instanceof Error ? error.message : String(error)
    return NextResponse.json({ 
      error: `Processing failed: ${errorMessage}`,
      processingTime: (Date.now() - startTime) / 1000
    }, { status: 500 })
  }
}