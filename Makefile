# =============================================================================
# Build, Install & Uninstall
# =============================================================================

build:

install: build
	./setup.py install

uninstall:
	rm -f $(DESTDIR)/usr/bin/argparse-tool

# =============================================================================
# Testing
# =============================================================================

test: ./argparse-tool.py ./argparse-tool-test.py bash.py fish.py zsh.py
	mkdir -p test
	./argparse-tool.py zsh  argparse-tool-test.py -o test/argparse-tool-test.zsh
	./argparse-tool.py bash argparse-tool-test.py -o test/argparse-tool-test.bash
	./argparse-tool.py fish argparse-tool-test.py -o test/argparse-tool-test.fish

install-test: build
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/zsh/site-functions
	mkdir -p $(DESTDIR)/usr/share/bash-completion/completions
	mkdir -p $(DESTDIR)/usr/share/fish/completions
	cp argparse-tool-test.py        $(DESTDIR)/usr/bin/argparse-tool-test
	cp test/argparse-tool-test.zsh  $(DESTDIR)/usr/share/zsh/site-functions/_argparse-tool-test
	cp test/argparse-tool-test.bash $(DESTDIR)/usr/share/bash-completion/completions/argparse-tool-test
	cp test/argparse-tool-test.fish $(DESTDIR)/usr/share/fish/completions/argparse-tool-test.fish
	# Notice: If zsh completion fails, remove ~/.zcompdump

uninstall-test:
	rm -f $(DESTDIR)/usr/bin/argparse-tool-test
	rm -f $(DESTDIR)/usr/share/zsh/site-functions/_argparse-tool-test
	rm -f $(DESTDIR)/usr/share/bash-completion/completions/argparse-tool-test
	rm -f $(DESTDIR)/usr/share/fish/completions/argparse-tool-test.fish

clean:
	rm -rf test argparse_tool.egg-info dist build 

