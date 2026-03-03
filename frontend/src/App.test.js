import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import VideoGeneratorApp from './App';

jest.mock('axios', () => ({
  get: jest.fn((url) => {
    if (url && url.includes('/styles')) {
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: { videos: [] } });
  }),
  post: jest.fn(() => Promise.resolve({ data: {} })),
}));

describe('VideoGeneratorApp', () => {
  test('renders without crashing', () => {
    render(<VideoGeneratorApp />);
  });

  test('displays the "AI Video Generator" header', () => {
    render(<VideoGeneratorApp />);
    expect(screen.getByText('AI Video Generator')).toBeInTheDocument();
  });

  test('renders "Text to Video" and "Image to Video" tab buttons', () => {
    render(<VideoGeneratorApp />);
    expect(screen.getByText('Text to Video')).toBeInTheDocument();
    expect(screen.getByText('Image to Video')).toBeInTheDocument();
  });

  test('renders the text prompt textarea in the default "text" tab', () => {
    render(<VideoGeneratorApp />);
    expect(
      screen.getByPlaceholderText(
        'A majestic dragon flying over a medieval castle at sunset...'
      )
    ).toBeInTheDocument();
  });

  test('"Generate Video" button is present but disabled when textarea is empty', () => {
    render(<VideoGeneratorApp />);
    const button = screen.getByRole('button', { name: /generate video/i });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  test('switching to "Image to Video" tab shows the upload area', () => {
    render(<VideoGeneratorApp />);
    fireEvent.click(screen.getByText('Image to Video'));
    expect(screen.getByText('Click to upload image')).toBeInTheDocument();
  });

  test('"Show Gallery" button is present in the header', () => {
    render(<VideoGeneratorApp />);
    expect(
      screen.getByRole('button', { name: /show gallery/i })
    ).toBeInTheDocument();
  });
});
