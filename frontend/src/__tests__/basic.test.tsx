/**
 * Frontend smoke tests for SENTINEL.
 *
 * Run with: npx jest --passWithNoTests
 * Or use the test script: npm test
 */

// Placeholder — add real component tests after setting up Jest with next/jest
describe('SENTINEL Frontend', () => {
  it('package.json defines expected dependencies', () => {
    const pkg = require('../../package.json')
    expect(pkg.dependencies.next).toBeDefined()
    expect(pkg.dependencies.react).toBeDefined()
    expect(pkg.dependencies['lucide-react']).toBeDefined()
    expect(pkg.dependencies.recharts).toBeDefined()
  })

  it('build script is defined', () => {
    const pkg = require('../../package.json')
    expect(pkg.scripts.build).toBe('next build')
  })
})
