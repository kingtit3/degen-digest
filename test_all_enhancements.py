#!/usr/bin/env python3
"""
Comprehensive Test Script for All Enhancements
Tests the complete enhanced viral prediction system
"""

import asyncio
import json
import time
import nest_asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Apply nest_asyncio for better async handling
nest_asyncio.apply()

from utils.advanced_logging import get_logger
from scripts.enhanced_data_pipeline import EnhancedDataPipeline
from scripts.automated_retraining import AutomatedRetraining
from utils.data_quality_monitor import DataQualityMonitor
from processor.enhanced_viral_predictor import enhanced_predictor

logger = get_logger(__name__)

class ComprehensiveTester:
    """Comprehensive test suite for all enhancements"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    async def run_all_tests(self):
        """Run all enhancement tests"""
        
        print("🚀 Starting Comprehensive Enhancement Tests")
        print("=" * 60)
        
        try:
            # Test 1: Enhanced Data Pipeline
            await self.test_enhanced_data_pipeline()
            
            # Test 2: Data Quality Monitoring
            await self.test_data_quality_monitoring()
            
            # Test 3: Enhanced Viral Predictor
            await self.test_enhanced_viral_predictor()
            
            # Test 4: Automated Retraining
            await self.test_automated_retraining()
            
            # Test 5: Integration Test
            await self.test_integration()
            
            # Generate final report
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
    
    async def test_enhanced_data_pipeline(self):
        """Test the enhanced data pipeline"""
        
        print("\n📊 Testing Enhanced Data Pipeline...")
        
        try:
            pipeline = EnhancedDataPipeline()
            
            # Run pipeline
            start_time = time.time()
            await pipeline.run_full_pipeline()
            pipeline_time = time.time() - start_time
            
            # Check results
            total_items = len(pipeline.processed_data)
            viral_predictions = len(pipeline.viral_predictions)
            data_sources = len(pipeline.data_sources)
            
            # Quality checks
            success = (
                total_items > 0 and
                viral_predictions > 0 and
                data_sources > 0 and
                pipeline_time < 300  # Should complete within 5 minutes
            )
            
            self.test_results['enhanced_data_pipeline'] = {
                'status': 'PASS' if success else 'FAIL',
                'total_items': total_items,
                'viral_predictions': viral_predictions,
                'data_sources': data_sources,
                'processing_time': pipeline_time,
                'details': {
                    'sources_with_data': [k for k, v in pipeline.data_sources.items() if v.get('count', 0) > 0],
                    'sources_with_errors': [k for k, v in pipeline.data_sources.items() if v.get('error')]
                }
            }
            
            print(f"✅ Enhanced Data Pipeline: {total_items} items, {viral_predictions} predictions, {pipeline_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Enhanced data pipeline test failed: {e}")
            self.test_results['enhanced_data_pipeline'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ Enhanced Data Pipeline: FAILED - {e}")
    
    async def test_data_quality_monitoring(self):
        """Test data quality monitoring"""
        
        print("\n🔍 Testing Data Quality Monitoring...")
        
        try:
            monitor = DataQualityMonitor()
            
            # Create sample data
            sample_data = [
                {
                    'text': 'Bitcoin is going to the moon! 🚀',
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'twitter',
                    'engagement_velocity': 10.5,
                    'viral_coefficient': 0.8,
                    'influence_score': 85.2
                },
                {
                    'text': 'Ethereum merge is amazing!',
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'reddit',
                    'engagement_velocity': 5.2,
                    'viral_coefficient': 0.3
                }
            ]
            
            # Test quality monitoring
            quality_report = monitor.monitor_data_quality(sample_data, 'test_source')
            quality_summary = monitor.get_quality_summary()
            recommendations = monitor.get_recommendations()
            
            # Save quality report
            monitor.save_quality_report()
            
            # Check results
            success = (
                quality_report['overall_score'] > 0.5 and
                'test_source' in quality_summary['source_status']
            )
            
            self.test_results['data_quality_monitoring'] = {
                'status': 'PASS' if success else 'FAIL',
                'quality_score': quality_report['overall_score'],
                'alerts': quality_report['alerts'],
                'recommendations': recommendations,
                'summary': quality_summary
            }
            
            print(f"✅ Data Quality Monitoring: Score {quality_report['overall_score']:.3f}, {len(quality_report['alerts'])} alerts")
            
        except Exception as e:
            logger.error(f"Data quality monitoring test failed: {e}")
            self.test_results['data_quality_monitoring'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ Data Quality Monitoring: FAILED - {e}")
    
    async def test_enhanced_viral_predictor(self):
        """Test enhanced viral predictor"""
        
        print("\n🤖 Testing Enhanced Viral Predictor...")
        
        try:
            # Create sample data for prediction
            sample_items = [
                {
                    'text': 'Bitcoin is going to the moon! 🚀',
                    'engagement_velocity': 10.5,
                    'viral_coefficient': 0.8,
                    'influence_score': 85.2,
                    'source': 'twitter',
                    'timestamp': datetime.utcnow().isoformat()
                },
                {
                    'text': 'New meme coin launching soon!',
                    'engagement_velocity': 25.0,
                    'viral_coefficient': 1.2,
                    'influence_score': 120.0,
                    'source': 'telegram',
                    'timestamp': datetime.utcnow().isoformat()
                }
            ]
            
            # Test predictions
            predictions = []
            for item in sample_items:
                try:
                    prediction = enhanced_predictor.predict_viral_score(item)
                    predictions.append(prediction)
                except Exception as e:
                    logger.warning(f"Failed to predict for item: {e}")
                    continue
            
            # Check results
            success = (
                len(predictions) > 0 and
                all('score' in pred for pred in predictions) and
                all(0 <= pred['score'] <= 1 for pred in predictions)
            )
            
            self.test_results['enhanced_viral_predictor'] = {
                'status': 'PASS' if success else 'FAIL',
                'predictions_made': len(predictions),
                'sample_predictions': predictions[:3],  # Show first 3 predictions
                'model_performance': enhanced_predictor.model_performance
            }
            
            print(f"✅ Enhanced Viral Predictor: {len(predictions)} predictions made")
            
        except Exception as e:
            logger.error(f"Enhanced viral predictor test failed: {e}")
            self.test_results['enhanced_viral_predictor'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ Enhanced Viral Predictor: FAILED - {e}")
    
    async def test_automated_retraining(self):
        """Test automated retraining system"""
        
        print("\n🔄 Testing Automated Retraining...")
        
        try:
            retraining_system = AutomatedRetraining()
            
            # Get retraining stats
            stats = retraining_system.get_retraining_stats()
            
            # Check if system is properly initialized
            success = (
                'total_retrains' in stats and
                'current_performance' in stats and
                'performance_trend' in stats
            )
            
            self.test_results['automated_retraining'] = {
                'status': 'PASS' if success else 'FAIL',
                'stats': stats,
                'config': retraining_system.retraining_config
            }
            
            print(f"✅ Automated Retraining: System initialized, {stats.get('total_retrains', 0)} retrains")
            
        except Exception as e:
            logger.error(f"Automated retraining test failed: {e}")
            self.test_results['automated_retraining'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ Automated Retraining: FAILED - {e}")
    
    async def test_integration(self):
        """Test integration of all components"""
        
        print("\n🔗 Testing Integration...")
        
        try:
            # Test end-to-end workflow
            pipeline = EnhancedDataPipeline()
            monitor = DataQualityMonitor()
            
            # Run pipeline
            await pipeline.run_full_pipeline()
            
            # Monitor quality for each source
            quality_reports = {}
            for source, data in pipeline.data_sources.items():
                if data.get('data'):
                    quality_report = monitor.monitor_data_quality(data['data'], source)
                    quality_reports[source] = quality_report
            
            # Generate predictions
            predictions = []
            for item in pipeline.processed_data[:10]:  # Test first 10 items
                try:
                    prediction = enhanced_predictor.predict_viral_score(item)
                    predictions.append(prediction)
                except Exception as e:
                    continue
            
            # Check integration success
            success = (
                len(pipeline.processed_data) > 0 and
                len(quality_reports) > 0 and
                len(predictions) > 0
            )
            
            self.test_results['integration'] = {
                'status': 'PASS' if success else 'FAIL',
                'pipeline_items': len(pipeline.processed_data),
                'quality_reports': len(quality_reports),
                'predictions_made': len(predictions),
                'overall_quality_score': monitor.get_quality_summary()['overall_score']
            }
            
            print(f"✅ Integration: {len(pipeline.processed_data)} items, {len(predictions)} predictions")
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            self.test_results['integration'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"❌ Integration: FAILED - {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\n📋 Generating Test Report...")
        
        # Calculate overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASS')
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Create report
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': success_rate,
                'test_duration': time.time() - self.start_time
            },
            'test_results': self.test_results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save report
        output_path = Path("output/enhanced_pipeline/test_report.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {time.time() - self.start_time:.2f} seconds")
        
        print("\n📊 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            status_icon = "✅" if status == 'PASS' else "❌"
            print(f"{status_icon} {test_name}: {status}")
            
            if status == 'FAIL' and 'error' in result:
                print(f"   Error: {result['error']}")
        
        print(f"\n📄 Full report saved to: {output_path}")
        
        if success_rate >= 80:
            print("\n🎉 All major enhancements are working! The system is ready for production.")
        elif success_rate >= 60:
            print("\n⚠️  Most enhancements are working, but some issues need attention.")
        else:
            print("\n🚨 Multiple issues detected. Please review and fix before deployment.")

async def main():
    """Main function to run comprehensive tests"""
    
    tester = ComprehensiveTester()
    
    try:
        await tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n💥 Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 