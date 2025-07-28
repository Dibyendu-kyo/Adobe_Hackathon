import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Basic health check
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      services: {
        api: 'operational',
        python: 'checking...'
      }
    }

    // Quick Python check
    try {
      const { spawn } = require('child_process')
      const python = spawn('python', ['--version'])
      
      python.on('close', (code: number) => {
        health.services.python = code === 0 ? 'operational' : 'error'
      })
      
      // Don't wait for Python check to complete
      setTimeout(() => {
        if (health.services.python === 'checking...') {
          health.services.python = 'timeout'
        }
      }, 1000)
      
    } catch (error) {
      health.services.python = 'error'
    }

    return NextResponse.json(health, { status: 200 })
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