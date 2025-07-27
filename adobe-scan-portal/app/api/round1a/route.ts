import { NextRequest, NextResponse } from 'next/server'
import { writeFile, unlink } from 'fs/promises'
import { join } from 'path'
import { tmpdir } from 'os'
import { randomUUID } from 'crypto'

// Import the Round 1A extractor
const { spawn } = require('child_process')
const path = require('path')

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'Only PDF files are supported' }, { status: 400 })
    }

    // Save the uploaded file temporarily
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    
    const tempId = randomUUID()
    const tempFilePath = join(tmpdir(), `upload_${tempId}.pdf`)
    
    await writeFile(tempFilePath, buffer)

    try {
      // Process with Round 1A Python script
      const startTime = Date.now()
      
      const result = await new Promise((resolve, reject) => {
        const pythonScript = path.join(process.cwd(), 'scripts', 'process_round1a.py')
        const python = spawn('python', [pythonScript, tempFilePath])
        
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
            reject(new Error(`Python script failed: ${error}`))
          }
        })
        
        python.on('error', (err) => {
          reject(new Error(`Failed to start Python process: ${err}`))
        })
      })

      const processingTime = (Date.now() - startTime) / 1000

      // Clean up temp file
      await unlink(tempFilePath)

      return NextResponse.json({
        success: true,
        processingTime,
        result,
        constraintsMet: {
          timeLimit: processingTime <= 10,
          formatValid: typeof result === 'object' && 'title' in result && 'outline' in result
        }
      })

    } catch (processingError) {
      // Clean up temp file on error
      try {
        await unlink(tempFilePath)
      } catch {}
      
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