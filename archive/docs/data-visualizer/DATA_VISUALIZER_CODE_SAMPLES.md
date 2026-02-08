# Data Visualizer - Code Samples & Starter Templates

## Quick Start Templates

### 1. Basic Chart Implementation
```typescript
// packages/core/src/charts/BarChart.ts
import { Chart, DataSet, ChartConfig } from '../types'
import { WebGPURenderer } from '../rendering/WebGPURenderer'

export class BarChart implements Chart {
  private renderer: WebGPURenderer
  private data: DataSet
  private config: ChartConfig

  constructor(canvas: HTMLCanvasElement, config: ChartConfig) {
    this.renderer = new WebGPURenderer(canvas)
    this.config = config
  }

  async render(data: DataSet): Promise<void> {
    this.data = data

    const vertices = this.generateVertices(data)
    const indices = this.generateIndices(data)

    await this.renderer.drawBars(vertices, indices, this.config)
  }

  private generateVertices(data: DataSet): Float32Array {
    const vertices = new Float32Array(data.points.length * 6) // x, y, r, g, b, a

    data.points.forEach((point, i) => {
      const baseIndex = i * 6
      vertices[baseIndex] = point.x
      vertices[baseIndex + 1] = point.y
      vertices[baseIndex + 2] = point.color.r
      vertices[baseIndex + 3] = point.color.g
      vertices[baseIndex + 4] = point.color.b
      vertices[baseIndex + 5] = point.color.a
    })

    return vertices
  }

  private generateIndices(data: DataSet): Uint32Array {
    const indices = new Uint32Array(data.points.length * 6) // 2 triangles per bar

    data.points.forEach((_, i) => {
      const baseIndex = i * 6
      const vertexIndex = i * 4 // 4 vertices per bar

      // First triangle
      indices[baseIndex] = vertexIndex
      indices[baseIndex + 1] = vertexIndex + 1
      indices[baseIndex + 2] = vertexIndex + 2

      // Second triangle
      indices[baseIndex + 3] = vertexIndex + 2
      indices[baseIndex + 4] = vertexIndex + 3
      indices[baseIndex + 5] = vertexIndex
    })

    return indices
  }

  async update(newData: Partial<DataSet>): Promise<void> {
    this.data = { ...this.data, ...newData }
    await this.render(this.data)
  }

  destroy(): void {
    this.renderer.destroy()
  }
}
```

### 2. AI-Powered Chart Generator
```typescript
// packages/ai/src/NLChartGenerator.ts
import * as tf from '@tensorflow/tfjs'
import { ChartConfig, DataSet, ChartType } from '../core/types'

export class NLChartGenerator {
  private model: tf.LayersModel
  private vocabulary: Map<string, number>

  constructor() {
    this.initializeModel()
    this.loadVocabulary()
  }

  private async initializeModel(): Promise<void> {
    // Create a simple sequence-to-sequence model for chart generation
    this.model = tf.sequential({
      layers: [
        tf.layers.embedding({ inputDim: 10000, outputDim: 128 }),
        tf.layers.lstm({ units: 64, returnSequences: true }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.lstm({ units: 32 }),
        tf.layers.dense({ units: 16, activation: 'relu' }),
        tf.layers.dense({ units: 6, activation: 'softmax' }) // Chart parameters
      ]
    })

    this.model.compile({
      optimizer: 'adam',
      loss: 'categoricalCrossentropy',
      metrics: ['accuracy']
    })
  }

  async generateChart(query: string): Promise<ChartConfig> {
    // Preprocess the query
    const processedQuery = this.preprocessQuery(query)
    const embedding = await this.generateEmbedding(processedQuery)

    // Predict chart configuration
    const prediction = this.model.predict(embedding) as tf.Tensor
    const chartParams = await prediction.data()

    // Extract chart type and parameters
    const chartType = this.extractChartType(chartParams)
    const dataMapping = this.extractDataMapping(chartParams)
    const styling = this.extractStyling(chartParams)

    return {
      type: chartType,
      dataMapping,
      styling,
      title: this.generateTitle(query),
      description: this.generateDescription(query)
    }
  }

  private preprocessQuery(query: string): string[] {
    // Tokenize and normalize the query
    return query.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 0)
  }

  private async generateEmbedding(tokens: string[]): Promise<tf.Tensor> {
    const indices = tokens.map(token => this.vocabulary.get(token) || 0)
    const padded = this.padSequence(indices, 50) // Max sequence length

    return tf.tensor2d([padded])
  }

  private extractChartType(params: Float32Array): ChartType {
    const types: ChartType[] = ['bar', 'line', 'pie', 'scatter', 'area', 'bubble']
    const maxIndex = params.indexOf(Math.max(...params))
    return types[maxIndex]
  }

  private extractDataMapping(params: Float32Array): DataMapping {
    // Extract data column mappings based on query analysis
    return {
      x: 'date',
      y: 'value',
      group: 'category',
      size: 'volume',
      color: 'region'
    }
  }

  private extractStyling(params: Float32Array): StylingConfig {
    return {
      colorScheme: 'viridis',
      animation: true,
      interactive: true,
      responsive: true
    }
  }
}
```

### 3. Real-Time Collaboration Engine
```typescript
// packages/collaboration/src/CollaborationEngine.ts
import * as Y from 'yjs'
import { WebRTCProvider } from 'y-webrtc'
import { Awareness } from 'y-protocols/awareness'

export interface CollaborationEvent {
  type: 'update' | 'join' | 'leave' | 'cursor'
  userId: string
  data: any
  timestamp: number
}

export class CollaborationEngine {
  private doc: Y.Doc
  private provider: WebRTCProvider
  private awareness: Awareness
  private eventListeners = new Map<string, Function[]>()
  private userId: string

  constructor(roomId: string, userId: string) {
    this.userId = userId
    this.doc = new Y.Doc()
    this.provider = new WebRTCProvider(roomId, this.doc)
    this.awareness = this.provider.awareness

    this.setupEventHandlers()
  }

  private setupEventHandlers(): void {
    // Handle document updates
    this.doc.on('update', (update: Uint8Array, origin: any) => {
      if (origin !== 'local') {
        this.emit('update', {
          type: 'update',
          userId: origin?.userId || 'unknown',
          data: update,
          timestamp: Date.now()
        })
      }
    })

    // Handle awareness changes (user presence)
    this.awareness.on('change', (changes: any) => {
      changes.added.forEach((userId: string) => {
        this.emit('join', {
          type: 'join',
          userId,
          data: this.awareness.getStates().get(userId),
          timestamp: Date.now()
        })
      })

      changes.removed.forEach((userId: string) => {
        this.emit('leave', {
          type: 'leave',
          userId,
          data: null,
          timestamp: Date.now()
        })
      })
    })

    // Handle cursor movements
    this.awareness.on('change', (changes: any) => {
      const states = this.awareness.getStates()
      states.forEach((state, userId) => {
        if (userId !== this.userId && state.cursor) {
          this.emit('cursor', {
            type: 'cursor',
            userId,
            data: state.cursor,
            timestamp: Date.now()
          })
        }
      })
    })
  }

  updateChart(chartId: string, updates: Partial<Chart>): void {
    const charts = this.doc.getMap('charts')
    const chart = charts.get(chartId) || {}

    // Apply updates using Yjs transactions for CRDT consistency
    this.doc.transact(() => {
      Object.entries(updates).forEach(([key, value]) => {
        if (value !== undefined) {
          chart[key] = value
        }
      })
      charts.set(chartId, chart)
    }, 'local')
  }

  updateCursor(position: { x: number; y: number }): void {
    this.awareness.setLocalStateField('cursor', {
      userId: this.userId,
      position,
      timestamp: Date.now()
    })
  }

  getUserList(): User[] {
    const states = this.awareness.getStates()
    return Array.from(states.entries()).map(([userId, state]) => ({
      id: userId,
      name: state.name || `User ${userId.slice(0, 8)}`,
      color: state.color || this.generateUserColor(userId),
      cursor: state.cursor,
      online: true
    }))
  }

  private generateUserColor(userId: string): string {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    return colors[hash % colors.length]
  }

  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(callback)
  }

  off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: CollaborationEvent): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => callback(data))
    }
  }

  destroy(): void {
    this.provider.destroy()
    this.doc.destroy()
  }
}
```

### 4. WebGPU Rendering Pipeline
```typescript
// packages/core/src/rendering/WebGPURenderer.ts
export class WebGPURenderer {
  private device: GPUDevice
  private context: GPUCanvasContext
  private pipeline: GPURenderPipeline
  private vertexBuffer: GPUBuffer
  private indexBuffer: GPUBuffer
  private uniformBuffer: GPUBuffer

  constructor(canvas: HTMLCanvasElement) {
    this.initializeWebGPU(canvas)
  }

  private async initializeWebGPU(canvas: HTMLCanvasElement): Promise<void> {
    // Get GPU adapter and device
    const adapter = await navigator.gpu.requestAdapter()
    if (!adapter) {
      throw new Error('WebGPU not supported')
    }

    this.device = await adapter.requestDevice()
    this.context = canvas.getContext('webgpu')!

    // Configure canvas context
    const presentationFormat = navigator.gpu.getPreferredCanvasFormat()
    this.context.configure({
      device: this.device,
      format: presentationFormat,
      alphaMode: 'premultiplied'
    })

    await this.createRenderPipeline(presentationFormat)
    this.createBuffers()
  }

  private async createRenderPipeline(format: GPUTextureFormat): Promise<void> {
    const vertexShader = `
      struct VertexInput {
        @location(0) position: vec2<f32>,
        @location(1) color: vec4<f32>,
      }

      struct VertexOutput {
        @builtin(position) clip_position: vec4<f32>,
        @location(0) color: vec4<f32>,
      }

      struct Uniforms {
        transform: mat3x3<f32>,
      }

      @group(0) @binding(0) var<uniform> uniforms: Uniforms;

      @vertex
      fn vs_main(vertex: VertexInput) -> VertexOutput {
        var output: VertexOutput;
        let transformed = uniforms.transform * vec3<f32>(vertex.position, 1.0);
        output.clip_position = vec4<f32>(transformed.xy, 0.0, 1.0);
        output.color = vertex.color;
        return output;
      }
    `

    const fragmentShader = `
      @fragment
      fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
        return input.color;
      }
    `

    const pipelineDescriptor: GPURenderPipelineDescriptor = {
      vertex: {
        module: this.device.createShaderModule({ code: vertexShader }),
        entryPoint: 'vs_main',
        buffers: [
          {
            arrayStride: 24, // 6 floats * 4 bytes
            attributes: [
              { shaderLocation: 0, offset: 0, format: 'float32x2' }, // position
              { shaderLocation: 1, offset: 8, format: 'float32x4' }  // color
            ]
          }
        ]
      },
      fragment: {
        module: this.device.createShaderModule({ code: fragmentShader }),
        entryPoint: 'fs_main',
        targets: [{ format }]
      },
      primitive: {
        topology: 'triangle-list',
        cullMode: 'back'
      },
      depthStencil: {
        depthWriteEnabled: true,
        depthCompare: 'less',
        format: 'depth24plus'
      },
      multisample: {
        count: 4
      }
    }

    this.pipeline = await this.device.createRenderPipelineAsync(pipelineDescriptor)
  }

  private createBuffers(): void {
    // Create vertex buffer
    this.vertexBuffer = this.device.createBuffer({
      size: 1024 * 1024, // 1MB
      usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST
    })

    // Create index buffer
    this.indexBuffer = this.device.createBuffer({
      size: 512 * 1024, // 512KB
      usage: GPUBufferUsage.INDEX | GPUBufferUsage.COPY_DST
    })

    // Create uniform buffer
    this.uniformBuffer = this.device.createBuffer({
      size: 192, // mat3x3 = 9 floats * 4 bytes * 4 (for alignment)
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
    })
  }

  async render(vertices: Float32Array, indices: Uint32Array, transform: Float32Array): Promise<void> {
    // Update buffers
    this.device.queue.writeBuffer(this.vertexBuffer, 0, vertices)
    this.device.queue.writeBuffer(this.indexBuffer, 0, indices)
    this.device.queue.writeBuffer(this.uniformBuffer, 0, transform)

    // Create command encoder
    const commandEncoder = this.device.createCommandEncoder()

    // Create render pass
    const textureView = this.context.getCurrentTexture().createView()
    const renderPass = commandEncoder.beginRenderPass({
      colorAttachments: [
        {
          view: textureView,
          clearValue: { r: 0.1, g: 0.1, b: 0.1, a: 1.0 },
          loadOp: 'clear',
          storeOp: 'store'
        }
      ]
    })

    // Set pipeline and bind resources
    renderPass.setPipeline(this.pipeline)
    renderPass.setVertexBuffer(0, this.vertexBuffer)
    renderPass.setIndexBuffer(this.indexBuffer, 'uint32')
    renderPass.setBindGroup(0, this.createBindGroup())

    // Draw
    renderPass.drawIndexed(indices.length)
    renderPass.end()

    // Submit commands
    this.device.queue.submit([commandEncoder.finish()])
  }

  private createBindGroup(): GPUBindGroup {
    const bindGroupLayout = this.pipeline.getBindGroupLayout(0)

    return this.device.createBindGroup({
      layout: bindGroupLayout,
      entries: [
        {
          binding: 0,
          resource: { buffer: this.uniformBuffer }
        }
      ]
    })
  }

  destroy(): void {
    this.vertexBuffer.destroy()
    this.indexBuffer.destroy()
    this.uniformBuffer.destroy()
  }
}
```

### 5. WebAssembly Data Processing
```rust
// packages/core/src/computation/data_processor.rs
use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct DataPoint {
    x: f64,
    y: f64,
    value: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct DataSet {
    points: Vec<DataPoint>,
    metadata: std::collections::HashMap<String, String>,
}

#[wasm_bindgen]
pub struct DataProcessor {
    data: Vec<DataPoint>,
}

#[wasm_bindgen]
impl DataProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new() -> DataProcessor {
        DataProcessor { data: Vec::new() }
    }

    #[wasm_bindgen]
    pub fn load_data(&mut self, json_data: &str) -> Result<(), JsValue> {
        let dataset: DataSet = serde_json::from_str(json_data)
            .map_err(|e| JsValue::from_str(&format!("JSON parsing error: {}", e)))?;

        self.data = dataset.points;
        Ok(())
    }

    #[wasm_bindgen]
    pub fn aggregate(&self, operation: &str) -> f64 {
        if self.data.is_empty() {
            return 0.0;
        }

        match operation {
            "sum" => self.data.iter().map(|p| p.value).sum(),
            "mean" => self.data.iter().map(|p| p.value).sum::<f64>() / self.data.len() as f64,
            "min" => self.data.iter().map(|p| p.value).fold(f64::INFINITY, f64::min),
            "max" => self.data.iter().map(|p| p.value).fold(f64::NEG_INFINITY, f64::max),
            "median" => self.calculate_median(),
            _ => 0.0
        }
    }

    #[wasm_bindgen]
    pub fn filter(&self, min_value: f64, max_value: f64) -> String {
        let filtered: Vec<DataPoint> = self.data.iter()
            .filter(|p| p.value >= min_value && p.value <= max_value)
            .cloned()
            .collect();

        serde_json::to_string(&filtered)
            .unwrap_or_else(|_| "[]".to_string())
    }

    #[wasm_bindgen]
    pub fn transform(&mut self, operation: &str) {
        match operation {
            "normalize" => self.normalize(),
            "log_transform" => self.log_transform(),
            "z_score" => self.z_score_normalization(),
            _ => {}
        }
    }

    #[wasm_bindgen]
    pub fn detect_outliers(&self, threshold: f64) -> String {
        let mean = self.aggregate("mean");
        let std_dev = self.calculate_std_dev(mean);

        let outliers: Vec<DataPoint> = self.data.iter()
            .filter(|p| (p.value - mean).abs() > threshold * std_dev)
            .cloned()
            .collect();

        serde_json::to_string(&outliers)
            .unwrap_or_else(|_| "[]".to_string())
    }

    #[wasm_bindgen]
    pub fn calculate_correlation(&self, x_column: &str, y_column: &str) -> f64 {
        // Simple Pearson correlation calculation
        if self.data.len() < 2 {
            return 0.0;
        }

        let n = self.data.len() as f64;
        let sum_x: f64 = self.data.iter().map(|p| p.x).sum();
        let sum_y: f64 = self.data.iter().map(|p| p.y).sum();
        let sum_xy: f64 = self.data.iter().map(|p| p.x * p.y).sum();
        let sum_x2: f64 = self.data.iter().map(|p| p.x * p.x).sum();
        let sum_y2: f64 = self.data.iter().map(|p| p.y * p.y).sum();

        let numerator = n * sum_xy - sum_x * sum_y;
        let denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)).sqrt();

        if denominator == 0.0 {
            0.0
        } else {
            numerator / denominator
        }
    }

    // Helper methods
    fn calculate_median(&self) -> f64 {
        let mut values: Vec<f64> = self.data.iter().map(|p| p.value).collect();
        values.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let len = values.len();
        if len % 2 == 0 {
            (values[len / 2 - 1] + values[len / 2]) / 2.0
        } else {
            values[len / 2]
        }
    }

    fn calculate_std_dev(&self, mean: f64) -> f64 {
        let variance = self.data.iter()
            .map(|p| (p.value - mean).powi(2))
            .sum::<f64>() / self.data.len() as f64;
        variance.sqrt()
    }

    fn normalize(&mut self) {
        if self.data.is_empty() { return; }

        let min_val = self.data.iter().map(|p| p.value).fold(f64::INFINITY, f64::min);
        let max_val = self.data.iter().map(|p| p.value).fold(f64::NEG_INFINITY, f64::max);
        let range = max_val - min_val;

        if range == 0.0 { return; }

        for point in &mut self.data {
            point.value = (point.value - min_val) / range;
        }
    }

    fn log_transform(&mut self) {
        for point in &mut self.data {
            point.value = point.value.log10().max(0.0);
        }
    }

    fn z_score_normalization(&mut self) {
        if self.data.is_empty() { return; }

        let mean = self.aggregate("mean");
        let std_dev = self.calculate_std_dev(mean);

        if std_dev == 0.0 { return; }

        for point in &mut self.data {
            point.value = (point.value - mean) / std_dev;
        }
    }
}

// Utility function to initialize the WASM module
#[wasm_bindgen(start)]
pub fn main() {
    console_error_panic_hook::set_once();
}
```

### 6. React Component Integration
```typescript
// packages/ui/src/components/Visualization.tsx
import React, { useRef, useEffect, useState, useCallback } from 'react'
import { BarChart } from '@data-visualizer/core'
import { CollaborationEngine } from '@data-visualizer/collaboration'
import { NLChartGenerator } from '@data-visualizer/ai'

interface VisualizationProps {
  data: any[]
  config?: any
  collaborative?: boolean
  aiEnabled?: boolean
  onChartUpdate?: (chart: any) => void
}

export const Visualization: React.FC<VisualizationProps> = ({
  data,
  config,
  collaborative = false,
  aiEnabled = false,
  onChartUpdate
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<BarChart>()
  const collaborationRef = useRef<CollaborationEngine>()
  const aiRef = useRef<NLChartGenerator>()

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const [query, setQuery] = useState('')

  // Initialize chart and services
  useEffect(() => {
    if (!canvasRef.current) return

    const initializeChart = async () => {
      try {
        setIsLoading(true)

        // Initialize chart
        chartRef.current = new BarChart(canvasRef.current, config || {})

        // Initialize collaboration if enabled
        if (collaborative) {
          collaborationRef.current = new CollaborationEngine(
            `room-${Date.now()}`,
            `user-${Math.random().toString(36).substr(2, 9)}`
          )

          collaborationRef.current.on('update', (event) => {
            onChartUpdate?.(event.data)
          })

          collaborationRef.current.on('join', (event) => {
            setUsers(prev => [...prev, event.data])
          })

          collaborationRef.current.on('leave', (event) => {
            setUsers(prev => prev.filter(u => u.id !== event.userId))
          })
        }

        // Initialize AI if enabled
        if (aiEnabled) {
          aiRef.current = new NLChartGenerator()
        }

        // Render initial chart
        await chartRef.current.render(data)

        setIsLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize chart')
        setIsLoading(false)
      }
    }

    initializeChart()

    return () => {
      chartRef.current?.destroy()
      collaborationRef.current?.destroy()
    }
  }, [collaborative, aiEnabled, config, onChartUpdate])

  // Handle data updates
  useEffect(() => {
    if (chartRef.current && !isLoading) {
      chartRef.current.update(data).catch(console.error)
    }
  }, [data, isLoading])

  // Handle AI queries
  const handleQuerySubmit = useCallback(async () => {
    if (!aiRef.current || !chartRef.current || !query.trim()) return

    try {
      setIsLoading(true)
      const chartConfig = await aiRef.current.generateChart(query)
      await chartRef.current.render(data)
      setQuery('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate chart')
    } finally {
      setIsLoading(false)
    }
  }, [query, data])

  // Handle canvas interactions
  const handleCanvasClick = useCallback((event: React.MouseEvent) => {
    if (!collaborationRef.current) return

    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return

    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    collaborationRef.current.updateCursor({ x, y })
  }, [])

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">{error}</div>
        <button onClick={() => setError(null)}>Retry</button>
      </div>
    )
  }

  return (
    <div className="visualization-container">
      {isLoading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}

      <canvas
        ref={canvasRef}
        className="visualization-canvas"
        onClick={handleCanvasClick}
        role="img"
        aria-label="Interactive data visualization"
      />

      {aiEnabled && (
        <div className="ai-controls">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask me anything about your data..."
            onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
          />
          <button onClick={handleQuerySubmit}>Generate</button>
        </div>
      )}

      {collaborative && users.length > 0 && (
        <div className="user-presence">
          <div className="user-list">
            {users.map(user => (
              <div key={user.id} className="user-avatar" style={{ backgroundColor: user.color }}>
                {user.name.charAt(0).toUpperCase()}
              </div>
            ))}
          </div>
          <span className="user-count">{users.length} users online</span>
        </div>
      )}
    </div>
  )
}
```

## Usage Examples

### Basic Usage
```typescript
import { Visualization } from '@data-visualizer/ui'

const App = () => {
  const data = [
    { x: 'Jan', y: 100, value: 100 },
    { x: 'Feb', y: 150, value: 150 },
    { x: 'Mar', y: 120, value: 120 },
    { x: 'Apr', y: 180, value: 180 }
  ]

  return (
    <Visualization
      data={data}
      config={{ type: 'bar', theme: 'dark' }}
      collaborative={true}
      aiEnabled={true}
    />
  )
}
```

### Advanced Usage with Custom Configuration
```typescript
const advancedConfig = {
  type: 'scatter',
  theme: 'custom',
  styling: {
    colorScheme: 'viridis',
    animation: true,
    interactive: true,
    responsive: true
  },
  axes: {
    x: { label: 'Time', type: 'temporal' },
    y: { label: 'Value', type: 'linear' }
  },
  tooltips: {
    enabled: true,
    format: (point) => `${point.x}: ${point.y.toFixed(2)}`
  }
}

<Visualization
  data={largeDataset}
  config={advancedConfig}
  collaborative={true}
  aiEnabled={true}
  onChartUpdate={(chart) => console.log('Chart updated:', chart)}
/>
```

These code samples provide a solid foundation for implementing the data visualizer with all the advanced features outlined in the specification.
