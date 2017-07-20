Usage example
#############

At first an instance of :py:class:`libsidplayfp.SidPlayfp` is required as it is the player interface.::

    >>> import libsidplayfp
    >>> player = libsidplayfp.SidPlayfp()

Usually at least a C64 Kernal ROM is required to play tunes (however some tunes can run without any ROMs). Some tunes also require BASIC and character generator ROMs. To supply the emulation with the required ROMs, :py:func:`libsidplayfp.SidPlayfp.set_roms` is used::

    >>> kernal = open('kernal.bin', 'rb').read()
    >>> # read other roms ...
    >>> player.set_roms(kernal)  # basic and character gen. ROMs are not required

Now the emulation only misses the most important part: the actual emulation engine. In this example we use the residfp emulation by using the :py:class:`libsidplayfp.ReSIDfpBuilder`::

    >>> emulation = libsidplayfp.ReSIDfpBuilder('residfp')
    >>> # create 2 emulated SID chips (for 2SID playback)
    >>> emulation.create(2)
    2

By passing a name, a new emulation instance is created. We also need to create some SID emulations. The PSID format currently supports tunes with up to three SIDs offering stereo output. The tune I choose to play requires two SID chips, so I created just two. Generally speaking you should create as much SID chips as required or supported (see :py:attr:`libsidplayfp.SidInfo.maxsids`).

Now ``player`` needs to be configured using ``emulation``. Several other options like stereo output and sampling frequency should also be configured::

    >>> config = player.config  # get the currently loaded SidConfig instance
    >>> config.sid_emulation = emulation
    >>> config.playback = libsidplayfp.Playback.STEREO
    >>> config.frequency = 44100
    >>> player.configure()  # configure the player/emulation

The last line configures the player. If something went wrong, an error will be raised (hopefully) explaining what failed. The error messages are passed from C++ implementation and wrapped into an Exception.

Finally a sidtune can be loaded. You can choose any tune you want, however I use "Phat Frog" from A-Man which is contained in the great `HVSC <http://hvsc.c64.org>`_. It is a stereo tune and does not require any ROM to be loaded.

    >>> tune = libsidplayfp.SidTune(b'Phat_Frog_2SID.sid')

To get some information about the tune :py:func:`libsidplayfp.SidTune.get_info()` can be used. This method returns a :py:class:`libsidplayfp.SidTuneInfo` instance containing information of the current selected subtune.

    >>> info = tune.get_info()
    >>> # get some info: title, author and release
    >>> info.info_strings
    [b'Phat Frog', b'Steven Diemer (A-Man)', b'2007 Xenon']

    >>> # number of subsongs:
    >>> info.songs
    1

    >>> # how many SID chips are used?
    >>> info.sid_chips
    2
    >>> # which models are required?
    >>> info.sid_model(0)
    <SidModel.MODEL8580: 2>
    >>> info.sid_model(1)
    <SidModel.MODEL8580: 2>

After loading the tune and receiving some information about it, we are ready to load it into the player.

    >>> player.load(tune)

If no exception is raised, everything is ready to play that tune. We just require some library to output the sound. Here we will use `PyAudio <https://pypi.python.org/pypi/PyAudio/>`_ but any audio library wil be sufficient if it supports 16 bit signed integer samples passed using a buffer.

Setup PyAudio::

    >>> import pyaudio
    >>> p = pyaudio.PyAudio()
    >>> stream = p.open(
    ...     format=pyaudio.paInt16, channels=2, rate=44100, output=True)

Create a buffer for 5000 samples (about 110 ms). It is important that this buffer is mutable as the player writes the sound output to it. Therefore a ``bytearray`` is used here.

    >>> samples = bytearray(5000 * 2)

And play 10 seconds::

    >>> while player.time < 10:
    ...     player.play(samples)
    ...     stream.write(bytes(samples))

If everything went fine you should hear some great music produced by the SID chip emulation. Enjoy!

After finishing playing around, you should close the stream and terminate PyAudio properly afterwards::

    >>> stream.close()
    >>> p.terminate()

