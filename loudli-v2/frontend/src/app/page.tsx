'use client'

import Link from 'next/link'
import { Mic2, TrendingUp, Users, DollarSign, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-accent-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Connect Podcasters with{' '}
              <span className="text-primary-600">Advertisers</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Loudli is the marketplace where podcast creators find sponsorship opportunities
              and brands reach engaged audiences through authentic podcast advertising.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link href="/register?type=podcaster">
                <Button size="lg">
                  I'm a Podcaster
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/register?type=advertiser">
                <Button size="lg" variant="outline">
                  I'm an Advertiser
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { icon: Mic2, label: 'Podcasts', value: '10,000+' },
              { icon: Users, label: 'Creators', value: '5,000+' },
              { icon: TrendingUp, label: 'Campaigns', value: '2,500+' },
              { icon: DollarSign, label: 'Paid Out', value: '$1M+' },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <stat.icon className="h-8 w-8 text-primary-600 mx-auto mb-3" />
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Whether you're a podcaster looking for sponsors or a brand seeking authentic
              reach, Loudli makes it easy.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* For Podcasters */}
            <Card>
              <CardContent className="p-8">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 text-primary-600 mb-6">
                  <Mic2 className="h-6 w-6" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">For Podcasters</h3>
                <ul className="space-y-4">
                  {[
                    'List your podcast and reach thousands of potential advertisers',
                    'Set your own rates and sponsorship preferences',
                    'Communicate directly with brands through our platform',
                    'Track campaign performance and grow your revenue',
                  ].map((item, i) => (
                    <li key={i} className="flex items-start">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center mr-3">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <span className="text-gray-600">{item}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/register?type=podcaster" className="mt-8 inline-block">
                  <Button>Start as Podcaster</Button>
                </Link>
              </CardContent>
            </Card>

            {/* For Advertisers */}
            <Card>
              <CardContent className="p-8">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent-100 text-accent-600 mb-6">
                  <TrendingUp className="h-6 w-6" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">For Advertisers</h3>
                <ul className="space-y-4">
                  {[
                    'Browse thousands of podcasts across all categories',
                    'Target your ideal audience by demographics and interests',
                    'Create campaigns and negotiate directly with creators',
                    'Track impressions, clicks, and campaign ROI',
                  ].map((item, i) => (
                    <li key={i} className="flex items-start">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center mr-3">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <span className="text-gray-600">{item}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/register?type=advertiser" className="mt-8 inline-block">
                  <Button variant="outline">Start as Advertiser</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Grow Your Podcast or Reach New Audiences?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of podcasters and advertisers already using Loudli.
          </p>
          <Link href="/register">
            <Button
              size="lg"
              className="bg-white text-primary-600 hover:bg-gray-100"
            >
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
