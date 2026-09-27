import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from './api'

describe('api client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('parses a successful JSON response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ is_demo: true, items: [] }),
      }),
    )
    const result = await api.stocks()
    expect(result.items).toEqual([])
  })

  it('throws ApiError with detail message on failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: "Unknown symbol 'FAKE'" }),
      }),
    )
    await expect(api.stock('FAKE')).rejects.toThrow(ApiError)
    await expect(api.stock('FAKE')).rejects.toThrow("Unknown symbol 'FAKE'")
  })
})
