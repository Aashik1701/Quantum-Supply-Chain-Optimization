'use client';

import React, { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle2, 
  Globe, 
  Package, 
  Truck, 
  Droplets,
  ArrowRight,
  Zap,
  Target,
  Shuffle,
  BarChart3,
  Cpu,
  Atom,
  TrendingUp,
  Clock,
  DollarSign,
  Leaf
} from 'lucide-react';
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

// Sample data for charts
const vqeConvergenceData = Array.from({ length: 20 }, (_, i) => ({
  iteration: i + 1,
  energy: 15 * Math.exp(-i / 5) + 2 + (Math.random() - 0.5) * 0.5,
}));

const qaoaData = Array.from({ length: 11 }, (_, i) => ({
  p: i,
  cost: i === 0 ? 100 : 100 - i * 5 - Math.random() * 10,
}));

const performanceData = [
  { metric: 'Cost Reduction', classical: 15, quantum: 35, hybrid: 45 },
  { metric: 'CO₂ Reduction', classical: 12, quantum: 28, hybrid: 40 },
  { metric: 'Time Optimization', classical: 20, quantum: 30, hybrid: 50 },
];

const applications = [
  {
    icon: <Globe className="w-8 h-8 text-blue-400" />,
    title: 'Global Logistics',
    description: 'Optimize international shipping routes, container loads, and multi-modal fleet management for maximum efficiency.',
  },
  {
    icon: <Package className="w-8 h-8 text-amber-400" />,
    title: 'E-commerce',
    description: 'Dramatically speed up last-mile delivery for giants like Flipkart and Amazon, reducing costs and delivery times.',
  },
  {
    icon: <Droplets className="w-8 h-8 text-cyan-400" />,
    title: 'Cold Chain Logistics',
    description: 'Ensure integrity for pharma and groceries by optimizing routes with strict temperature and timing constraints.',
  },
  {
    icon: <Truck className="w-8 h-8 text-green-400" />,
    title: 'Sustainable Transport',
    description: 'Minimize CO₂ emissions by optimizing vehicle types, routes, and load factors for greener supply chains.',
  },
];

const problems = [
  'Warehouse capacity planning',
  'Complex vehicle routing',
  'Strict delivery windows',
  'Dynamic demand variability',
  'Multi-modal transportation',
  'Real-time optimization',
  'Carbon footprint tracking',
  'Resource allocation',
];

const HomePage: React.FC = () => {
  const [gamma, setGamma] = useState([0.5]);
  const [beta, setBeta] = useState([0.5]);

  const displayedQaoaData = useMemo(() => {
    const depth = Math.round((gamma[0] + beta[0]) * 5);
    return qaoaData.slice(0, depth + 1);
  }, [gamma, beta]);

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background provided by Layout via route config */}
      
      {/* Hero Section */}
      <section className="container relative z-20 px-4 py-16 mx-auto">
        <div className="mb-12 text-center">
          <div className="mb-6">
            <Badge variant="outline" className="mb-4 bg-primary/10 text-primary border-primary/20">
              Quantum-Enhanced Supply Chain
            </Badge>
          </div>
          <h1 className="mb-6 text-6xl font-bold leading-tight text-white">
            <span className="text-transparent bg-gradient-to-br from-gray-200 to-gray-400 bg-clip-text">tor</span>
            <span className="text-transparent bg-gradient-to-br from-primary to-teal-300 bg-clip-text">Que</span>
          </h1>
          <h2 className="mb-6 text-3xl font-semibold text-gray-200">
            Hybrid Quantum-Classical Supply Chain Optimization
          </h2>
          <p className="max-w-4xl mx-auto text-xl leading-relaxed text-gray-300">
            Revolutionary supply chain optimization platform that combines quantum computing algorithms 
            with classical optimization techniques to achieve superior performance in cost reduction, 
            carbon footprint minimization, and delivery time optimization.
          </p>
        </div>

        {/* Key Features Cards */}
        <div className="grid gap-8 mb-16 md:grid-cols-3">
          <Card className="transition-all bg-slate-800/90 border-slate-700 backdrop-blur-sm hover:bg-slate-700/90 hover:scale-105">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 mb-4 border border-blue-600 rounded-lg bg-blue-900/50">
                <Atom className="text-2xl text-blue-400" />
              </div>
              <CardTitle className="text-slate-200">Quantum-Enhanced Optimization</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300">
                Leverage QAOA (Quantum Approximate Optimization Algorithm) for combinatorial route selection
              </p>
            </CardContent>
          </Card>

          <Card className="transition-all bg-slate-800/90 border-slate-700 backdrop-blur-sm hover:bg-slate-700/90 hover:scale-105">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 mb-4 border border-purple-600 rounded-lg bg-purple-900/50">
                <Target className="text-2xl text-purple-400" />
              </div>
              <CardTitle className="text-slate-200">Classical Linear Programming</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300">
                Robust optimization using OR-Tools and PuLP for continuous variables
              </p>
            </CardContent>
          </Card>

          <Card className="transition-all bg-slate-800/90 border-slate-700 backdrop-blur-sm hover:bg-slate-700/90 hover:scale-105">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 mb-4 border border-green-600 rounded-lg bg-green-900/50">
                <Shuffle className="text-2xl text-green-400" />
              </div>
              <CardTitle className="text-slate-200">Hybrid Architecture</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-300">
                Intelligent combination of quantum and classical approaches for optimal performance
              </p>
            </CardContent>
          </Card>
        </div>

        {/* CTA Buttons */}
        <div className="mb-20 text-center">
          <Button size="lg" className="mr-4 bg-primary hover:bg-primary/90 text-primary-foreground transition-all hover:shadow-[0_0_20px] hover:shadow-primary/50">
            Get Started <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
          <Button size="lg" variant="outline" className="text-gray-200 border-gray-400 hover:bg-gray-800/50">
            View Demo
          </Button>
        </div>
      </section>

  {/* Problem and Mission Section */}
      <section className="relative z-20 py-20 bg-background/95 backdrop-blur-sm">
        <div className="container px-4 mx-auto">
          <div className="mb-16 text-center">
            <Badge variant="outline" className="mb-4 bg-primary/10 text-primary border-primary/20">
              The Challenge
            </Badge>
            <h2 className="mb-6 text-4xl font-bold">
              Today's supply chains are complex.
              <br />
              <span className="text-primary">We bring quantum precision to global logistics.</span>
            </h2>
          </div>

          <div className="grid gap-8 mb-16 md:grid-cols-2 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary" />
                  Our Mission
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Our mission is to pioneer hybrid quantum-classical optimization for next-generation supply chains. 
                  We tackle problems previously considered unsolvable, unlocking unprecedented efficiency and sustainability.
                </p>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  The Problem Space
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-x-6 gap-y-4">
                {problems.map((problem) => (
                  <div key={problem} className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-primary" />
                    <span className="text-muted-foreground">{problem}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Algorithms Section */}
      <section className="relative z-20 py-20 bg-card/50">
        <div className="container px-4 mx-auto">
          <div className="mb-16 text-center">
            <Badge variant="outline" className="mb-4 bg-primary/10 text-primary border-primary/20">
              The Quantum Engine
            </Badge>
            <h2 className="mb-6 text-4xl font-bold">Our Hybrid Optimization Core</h2>
            <p className="max-w-3xl mx-auto text-lg text-muted-foreground">
              We leverage cutting-edge quantum and classical algorithms to solve complex supply chain puzzles. 
              Explore how our core technologies work.
            </p>
          </div>

          <div className="grid gap-8 mb-16 lg:grid-cols-2">
            {/* QAOA Interactive Demo */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-primary" />
                  QAOA Performance
                </CardTitle>
                <CardDescription>
                  Quantum Approximate Optimization Algorithm for route selection
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6 space-y-4">
                  <div>
                    <Label htmlFor="gamma">Gamma Parameter: {gamma[0].toFixed(2)}</Label>
                    <Slider
                      id="gamma"
                      min={0}
                      max={1}
                      step={0.01}
                      value={gamma}
                      onValueChange={setGamma}
                      className="mt-2"
                    />
                  </div>
                  <div>
                    <Label htmlFor="beta">Beta Parameter: {beta[0].toFixed(2)}</Label>
                    <Slider
                      id="beta"
                      min={0}
                      max={1}
                      step={0.01}
                      value={beta}
                      onValueChange={setBeta}
                      className="mt-2"
                    />
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={displayedQaoaData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="p" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="cost" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* VQE Convergence */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  VQE Convergence
                </CardTitle>
                <CardDescription>
                  Variational Quantum Eigensolver for cost optimization
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={vqeConvergenceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="iteration" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="energy" stroke="#82ca9d" fill="#82ca9d" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Performance Comparison */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Quantum vs Classical Performance
              </CardTitle>
              <CardDescription>
                Comparative analysis of optimization approaches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="classical" fill="#8884d8" name="Classical" />
                  <Bar dataKey="quantum" fill="#82ca9d" name="Quantum" />
                  <Bar dataKey="hybrid" fill="#ffc658" name="Hybrid" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Applications Section */}
      <section className="relative z-20 py-20 bg-background/95">
        <div className="container px-4 mx-auto">
          <div className="mb-16 text-center">
            <Badge variant="outline" className="mb-4 bg-primary/10 text-primary border-primary/20">
              Real-World Impact
            </Badge>
            <h2 className="mb-6 text-4xl font-bold">From Quantum Theory to Business Reality</h2>
            <p className="max-w-3xl mx-auto text-lg text-muted-foreground">
              Our platform is designed to tackle tangible, high-value problems across various industries, 
              with a special focus on the unique challenges of the Indian market.
            </p>
          </div>

          <div className="grid gap-6 mb-16 sm:grid-cols-2 lg:grid-cols-4">
            {applications.map((app) => (
              <Card key={app.title} className="text-center transition-all hover:-translate-y-2 hover:shadow-lg hover:shadow-primary/10">
                <CardHeader className="items-center">
                  <div className="flex items-center justify-center w-16 h-16 rounded-lg bg-card ring-2 ring-border">
                    {app.icon}
                  </div>
                  <CardTitle className="mt-4">{app.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{app.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Key Benefits */}
          <div className="grid gap-6 md:grid-cols-3">
            <Card className="text-center">
              <CardHeader>
                <DollarSign className="w-12 h-12 mx-auto mb-4 text-green-500" />
                <CardTitle>45% Cost Reduction</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Achieve unprecedented cost savings through optimized routing and resource allocation.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Clock className="w-12 h-12 mx-auto mb-4 text-blue-500" />
                <CardTitle>50% Faster Delivery</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Reduce delivery times with quantum-optimized route planning and real-time adjustments.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Leaf className="w-12 h-12 mx-auto mb-4 text-green-600" />
                <CardTitle>40% CO₂ Reduction</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Minimize environmental impact through sustainable transportation optimization.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="relative z-20 py-20 bg-card/50">
        <div className="container px-4 mx-auto text-center">
          <h2 className="mb-6 text-4xl font-bold">Ready to Transform Your Supply Chain?</h2>
          <p className="max-w-2xl mx-auto mb-8 text-lg text-muted-foreground">
            Join the quantum revolution in logistics. Start optimizing your supply chain with cutting-edge 
            quantum-classical hybrid algorithms today.
          </p>
          <div className="flex justify-center gap-4">
            <Button size="lg" className="bg-primary hover:bg-primary/90">
              Start Free Trial <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button size="lg" variant="outline">
              Schedule Demo
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
