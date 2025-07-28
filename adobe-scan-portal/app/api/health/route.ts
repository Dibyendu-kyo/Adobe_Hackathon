import { NextResponse } from 'next/server'
import { existsSync } from 'fs'
import { join } from 'path'

export async function GET() {
  try {
    // Check if Python scripts exist
    const round1aScript = join(process.cwd(), 'scripts', 'process_round1a.py')
    const round1bScript = join(process.cwd(), 'scripts', 'process_round1b.py')
    
    // Check if models exist
    const modelsPath = join(process.cwd(), '..', 'models')
    const modelExists = existsSync(join(modelsPath, 'all-MiniLM-L6-v2'))
    
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        frontend: 'running',
        round1a: existsSync(round1aScript) ? 'available' : 'missing',
        round1b: existsSync(round1bScript) ? 'available' : 'missing',
        models: modelExists ? 'loaded' : 'missing'
      },
      version: process.env.npm_package_version || '1.0.0'
    }

    return NextResponse.json(health)
  } catch (error) {
    return NextResponse.json(
      { 
        status: 'unhealthy', 
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      }, 
      { status: 500 }
    )
  }
}